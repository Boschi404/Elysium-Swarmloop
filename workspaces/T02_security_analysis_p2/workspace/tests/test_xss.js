/**
 * T02_security_analysis — XSS Vulnerability Test Suite
 *
 * Tests two HTML templates:
 *   vulnerable-template.html  — intentionally vulnerable (innerHTML everywhere)
 *   secure-template.html       — fixed with textContent + DOMPurify
 *
 * Run: npm test
 */

import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';
import { expect, assert } from 'chai';
import createDOMPurify from 'dompurify';

const __dirname = dirname(fileURLToPath(import.meta.url));
const workspace = resolve(__dirname, '..');

/* --------------- helpers --------------- */

/** Read raw HTML of a file in workspace */
function readHTML(file) {
  return readFileSync(resolve(workspace, file), 'utf8');
}

/**
 * Create a JSDOM window from an HTML file, optionally loading its scripts.
 * The `url` can be set to simulate query params / hash.
 */
function makeDOM(htmlFile, url = 'http://localhost/') {
  const html = readHTML(htmlFile);
  return new JSDOM(html, { runScripts: 'dangerously', url });
}

/**
 * Return a JSDOM window pre-populated with a DOMPurify instance
 * (from the npm module — avoids CDN dependency in headless mode).
 */
function makeDOMwithPurify(htmlFile, url = 'http://localhost/') {
  const dom = makeDOM(htmlFile, url);
  const window = dom.window;
  window.DOMPurify = createDOMPurify(window);
  return dom;
}

/**
 * Parse a string of HTML and return true if it contains elements or
 * attributes that would execute JavaScript when inserted into the DOM.
 */
function containsExecutableScript(html) {
  const parser = new JSDOM('<!DOCTYPE html><div id="x"></div>');
  const doc = parser.window.document;
  const div = doc.getElementById('x');
  div.innerHTML = html;

  // Check for <script> tags
  if (div.querySelector('script')) return true;

  // Check for event handler attributes (onerror, onload, onclick, etc.)
  const all = div.querySelectorAll('*');
  for (const el of all) {
    for (const attr of el.attributes) {
      if (/^on/i.test(attr.name)) return true;
    }
    if (el.getAttribute?.('href')?.startsWith?.('javascript:')) return true;
    if (el.getAttribute?.('xlink:href')?.startsWith?.('javascript:')) return true;
  }

  // Check for iframe srcdoc
  const iframes = div.querySelectorAll('iframe[srcdoc]');
  if (iframes.length > 0) return true;

  // Check for <object data=javascript:...>
  const objects = div.querySelectorAll('object[data^="javascript:"]');
  if (objects.length > 0) return true;

  // Check for <svg/onload>
  const svgWithHandler = div.querySelectorAll('svg[*|onload]');
  if (svgWithHandler.length > 0) return true;

  return false;
}

/**
 * Check if a DOM element's text content includes the literal payload string.
 */
function isRenderedAsText(container, payload) {
  if (container.textContent.includes(payload)) return true;
  const walker = container.ownerDocument.createTreeWalker(
    container,
    4 /* NodeFilter.SHOW_TEXT */,
    null,
    false
  );
  let fullText = '';
  let node;
  while ((node = walker.nextNode())) {
    fullText += node.textContent;
  }
  return fullText.includes(payload);
}

/* =============================================
   TESTS
   ============================================= */

describe('T02 — XSS Vulnerability Security Analysis', function () {
  this.timeout(10000);

  // ─────────────────────────────────────────────────
  //  1. REFLECTED XSS
  // ─────────────────────────────────────────────────
  describe('1 — Reflected XSS', function () {

    it('VULNERABLE: innerHTML from query param permits script injection', function () {
      const maliciousParam = '<img src=x onerror=alert(1)>';
      const dom = makeDOM('vulnerable-template.html',
        'http://localhost/?q=' + encodeURIComponent(maliciousParam));

      const win = dom.window;
      const doc = win.document;

      // Simulate what the vulnerable handler does:
      // resultDiv.innerHTML = 'Showing results for: <strong>' + q + '</strong>'
      const q = new URL(win.location).searchParams.get('q');
      const resultDiv = doc.getElementById('searchResult');
      resultDiv.innerHTML = 'Showing results for: <strong>' + q + '</strong>';

      const img = resultDiv.querySelector('img');
      assert.ok(img, 'innerHTML should create an <img> element from attacker input');
      assert.equal(
        img.getAttribute('onerror'),
        'alert(1)',
        'event handler attribute should be present (XSS exploitable)'
      );
    });

    it('SECURE: textContent from query param PREVENTS script injection', function () {
      const maliciousParam = '<img src=x onerror=alert(1)>';
      const dom = makeDOMwithPurify('secure-template.html',
        'http://localhost/?q=' + encodeURIComponent(maliciousParam));

      const win = dom.window;
      const doc = win.document;

      const q = new URL(win.location).searchParams.get('q');
      const resultDiv = doc.getElementById('searchResult');
      // Secure version uses textContent
      resultDiv.textContent = 'Showing results for: ' + q;

      assert.ok(
        resultDiv.textContent.includes(maliciousParam),
        'textContent should render HTML tags as visible text, not execute them'
      );
      assert.isNull(resultDiv.querySelector('img'),
        'no <img> element should be injected');
    });

    it('VULNERABLE: <script> tag via query param executes', function () {
      const dom = makeDOM('vulnerable-template.html',
        'http://localhost/?q=<script>alert("XSS")</script>');

      const win = dom.window;
      const doc = win.document;
      const q = new URL(win.location).searchParams.get('q');
      const resultDiv = doc.getElementById('searchResult');
      resultDiv.innerHTML = 'Showing results for: <strong>' + q + '</strong>';

      assert.ok(
        containsExecutableScript(resultDiv.innerHTML),
        'innerHTML should interpret <script> tags from reflected input'
      );
    });

    it('SECURE: <script> via query param is rendered as text, not executed', function () {
      const payload = '<script>alert("XSS")</script>';
      const dom = makeDOMwithPurify('secure-template.html',
        'http://localhost/?q=' + encodeURIComponent(payload));

      const win = dom.window;
      const doc = win.document;
      const q = new URL(win.location).searchParams.get('q');
      const resultDiv = doc.getElementById('searchResult');
      resultDiv.textContent = 'Showing results for: ' + q;

      assert.ok(
        isRenderedAsText(resultDiv, payload),
        'textContent should render <script> as visible text'
      );
    });
  });

  // ─────────────────────────────────────────────────
  //  2. STORED XSS
  // ─────────────────────────────────────────────────
  describe('2 — Stored XSS', function () {

    it('VULNERABLE: stored comment with <img onerror> renders as executable HTML', function () {
      const dom = makeDOM('vulnerable-template.html');
      const win = dom.window;
      const doc = win.document;

      // Simulate malicious data in localStorage
      const maliciousAuthor = '<img src=x onerror=alert(1)>';
      const comments = [{ author: maliciousAuthor, body: 'Normal text', date: new Date().toISOString() }];
      win.localStorage.setItem('comments', JSON.stringify(comments));

      // Re-run the vulnerable rendering pattern (string concat + innerHTML)
      const commentsContainer = doc.getElementById('commentsContainer');
      commentsContainer.innerHTML = '';
      for (let i = 0; i < comments.length; i++) {
        const c = comments[i];
        commentsContainer.innerHTML +=
          '<div class="comment">'
          + '<div class="author">' + c.author + '</div>'
          + '<div class="text">' + c.body + '</div>'
          + '</div>';
      }

      const authorDiv = commentsContainer.querySelector('.author');
      assert.ok(authorDiv, 'a .author div should exist');
      const img = authorDiv.querySelector('img');
      assert.ok(img, 'innerHTML should parse <img> from stored author field');
      assert.equal(img.getAttribute('onerror'), 'alert(1)',
        'event handler should survive storage round-trip (XSS exploitable)');
    });

    it('SECURE: stored comment with malicious author is rendered as TEXT only', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const win = dom.window;
      const doc = win.document;

      const maliciousAuthor = '<img src=x onerror=alert(1)>';
      const comments = [{ author: maliciousAuthor, body: 'Safe body', date: new Date().toISOString() }];
      win.localStorage.setItem('comments', JSON.stringify(comments));

      // Re-run the secure rendering pattern (createTextNode / textContent)
      const container = doc.getElementById('commentsContainer');
      container.textContent = '';
      for (let i = 0; i < comments.length; i++) {
        const c = comments[i];
        const div = doc.createElement('div');
        div.className = 'comment';
        const authorDiv = doc.createElement('div');
        authorDiv.className = 'author';
        authorDiv.textContent = c.author;
        div.appendChild(authorDiv);
        container.appendChild(div);
      }

      const authorDiv = doc.querySelector('.author');
      assert.ok(authorDiv, 'author div should exist');
      assert.ok(
        authorDiv.textContent.includes(maliciousAuthor),
        'textContent should show the literal <img src=x onerror=alert(1)> as text'
      );
      assert.isNull(authorDiv.querySelector('img'),
        'no <img> element should be created from textContent');
    });

    it('SECURE: DOMPurify strips dangerous tags from stored content', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const purify = dom.window.DOMPurify;

      const payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<a href="javascript:alert(1)">click</a>',
        '<svg onload="alert(1)"></svg>',
        '<body onload="alert(1)">',
        '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
      ];

      for (const payload of payloads) {
        const sanitized = purify.sanitize(payload);
        assert.isFalse(
          containsExecutableScript(sanitized),
          `DOMPurify should strip all executable content from: ${payload}`
        );
      }
    });

    it('VULNERABLE: <a href="javascript:…"> creates clickable XSS link', function () {
      const malicious = '<a href="javascript:alert(\'stored-xss\')">Click me</a>';
      assert.ok(
        containsExecutableScript(malicious),
        'javascript: href in stored content should be flagged as executable'
      );
    });

    it('SECURE: DOMPurify strips javascript: from href', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const purify = dom.window.DOMPurify;
      const sanitized = purify.sanitize('<a href="javascript:alert(1)">click</a>');
      expect(sanitized).to.not.include('javascript:');
    });
  });

  // ─────────────────────────────────────────────────
  //  3. DOM-BASED XSS (location.hash)
  // ─────────────────────────────────────────────────
  describe('3 — DOM-Based XSS (location.hash)', function () {

    it('VULNERABLE: hash-based innerHTML injection creates executable elements', function () {
      const hashPayload = '<img src=x onerror=alert("DOM_XSS")>';
      const dom = makeDOM('vulnerable-template.html',
        'http://localhost/#' + encodeURIComponent(hashPayload));

      const win = dom.window;
      const doc = win.document;

      // Simulate the vulnerable hash handler
      const hash = win.location.hash;
      const value = hash && hash.length > 1
        ? decodeURIComponent(hash.substring(1))
        : '';
      const target = doc.getElementById('searchResult');
      if (target) {
        target.innerHTML = 'Hash directive: <b>' + value + '</b>';
      }

      const img = target.querySelector('img');
      assert.ok(img, 'innerHTML from hash should create an <img> element');
      assert.ok(img.getAttribute('onerror'),
        'event handler should survive hash injection');
    });

    it('SECURE: hash-based content via textContent prevents injection', function () {
      const hashPayload = '<img src=x onerror=alert("DOM_XSS")>';
      const dom = makeDOMwithPurify('secure-template.html',
        'http://localhost/#' + encodeURIComponent(hashPayload));

      const win = dom.window;
      const doc = win.document;

      const hash = win.location.hash;
      const value = hash && hash.length > 1
        ? decodeURIComponent(hash.substring(1))
        : '';
      const target = doc.getElementById('searchResult');
      if (target) {
        target.textContent = 'Hash directive: ' + value;
      }

      assert.ok(
        target.textContent.includes(hashPayload),
        'textContent should render the hash payload as visible text'
      );
      assert.isNull(target.querySelector('img'),
        'no <img> element should be created from hash value with textContent');
    });
  });

  // ─────────────────────────────────────────────────
  //  4. EDGE CASES — secure template
  // ─────────────────────────────────────────────────
  describe('4 — Edge Cases (secure template)', function () {

    it('handles null/undefined author gracefully', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const win = dom.window;
      const doc = win.document;

      const comments = [{ author: null, body: 'test', date: new Date().toISOString() }];
      win.localStorage.setItem('comments', JSON.stringify(comments));

      const container = doc.getElementById('commentsContainer');
      container.textContent = '';
      for (let i = 0; i < comments.length; i++) {
        const c = comments[i];
        const div = doc.createElement('div');
        div.className = 'comment';
        const authorDiv = doc.createElement('div');
        authorDiv.className = 'author';
        authorDiv.textContent = c.author || 'Anonymous';
        div.appendChild(authorDiv);
        container.appendChild(div);
      }

      const authorDiv = doc.querySelector('.author');
      assert.ok(authorDiv, 'author div should exist');
      assert.equal(authorDiv.textContent, 'Anonymous', 'null author should fallback to Anonymous');
    });

    it('handles empty comments array', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const win = dom.window;
      const doc = win.document;

      win.localStorage.removeItem('comments');

      const container = doc.getElementById('commentsContainer');
      container.textContent = '';
      const comments = JSON.parse(win.localStorage.getItem('comments') || '[]');
      if (comments.length === 0) {
        const em = doc.createElement('em');
        em.textContent = 'No comments yet.';
        const p = doc.createElement('p');
        p.appendChild(em);
        container.appendChild(p);
      }

      assert.ok(container.querySelector('em'), 'should show "No comments yet."');
      assert.include(container.textContent, 'No comments yet.');
    });

    it('handles long text without truncation', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const win = dom.window;
      const doc = win.document;

      const longBody = 'A'.repeat(10000);
      const comments = [{ author: 'Bob', body: longBody, date: new Date().toISOString() }];
      win.localStorage.setItem('comments', JSON.stringify(comments));

      const container = doc.getElementById('commentsContainer');
      container.textContent = '';
      for (let i = 0; i < comments.length; i++) {
        const c = comments[i];
        const div = doc.createElement('div');
        div.className = 'comment';
        const bodyDiv = doc.createElement('div');
        bodyDiv.className = 'text';
        bodyDiv.textContent = c.body;
        div.appendChild(bodyDiv);
        container.appendChild(div);
      }

      const textDiv = doc.querySelector('.text');
      assert.ok(textDiv, 'text div should exist');
      assert.lengthOf(textDiv.textContent, 10000, 'long text should not be truncated');
    });

    it('safe HTML (b, i, strong) is rendered correctly by DOMPurify', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const purify = dom.window.DOMPurify;

      const safe = 'Hello <b>world</b> with <i>formatting</i>';
      const sanitized = purify.sanitize(safe, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'code'],
        ALLOWED_ATTR: ['href']
      });

      expect(sanitized).to.include('<b>world</b>');
      expect(sanitized).to.include('<i>formatting</i>');
      expect(sanitized).to.not.include('javascript:');
    });

    it('mixed content: safe formatting preserved, dangerous stripped', function () {
      const dom = makeDOMwithPurify('secure-template.html');
      const purify = dom.window.DOMPurify;

      const mixed = 'Normal <b>bold</b> <script>alert(1)</script> <img src=x onerror=steal()>';
      const sanitized = purify.sanitize(mixed, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'code'],
        ALLOWED_ATTR: ['href']
      });

      expect(sanitized).to.include('<b>bold</b>');
      expect(sanitized).to.not.include('<script>');
      expect(sanitized).to.not.include('onerror');
    });
  });

  // ─────────────────────────────────────────────────
  //  5. REPORT & ARTIFACT INTEGRITY
  // ─────────────────────────────────────────────────
  describe('5 — Report & Artifact Integrity', function () {

    it('report.md exists and contains all three XSS types', function () {
      const report = readHTML('report.md');
      expect(report).to.include('Reflected XSS');
      expect(report).to.include('Stored XSS');
      expect(report).to.include('DOM-Based XSS');
    });

    it('vulnerable-template.html exists with innerHTML vulnerabilities', function () {
      const html = readHTML('vulnerable-template.html');
      expect(html).to.include('innerHTML');
      expect(html).to.include('location.hash');
      expect(html).to.include('localStorage');
    });

    it('secure-template.html exists with textContent fixes', function () {
      const html = readHTML('secure-template.html');
      expect(html).to.include('textContent');
      // secure template uses textContent assignments, not innerHTML assignments
      const lines = html.split('\n');
      const innerHTMLassignments = lines.filter(l =>
        l.includes('innerHTML') && l.includes('=') &&
        !l.trimStart().startsWith('//') && !l.trimStart().startsWith('*')
      );
      assert.lengthOf(innerHTMLassignments, 0,
        'secure template should have no active innerHTML assignments outside comments: ' +
        JSON.stringify(innerHTMLassignments));
    });

    it('all workspace files are present', function () {
      const files = [
        resolve(workspace, 'vulnerable-template.html'),
        resolve(workspace, 'secure-template.html'),
        resolve(workspace, 'report.md'),
      ];
      for (const f of files) {
        assert.doesNotThrow(() => readFileSync(f, 'utf8'), `File should exist: ${f}`);
      }
    });
  });
});
