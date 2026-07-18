# T02 Security Analysis — XSS Vulnerability Review

## Solution Summary

This solution analyzes a sample guestbook web application for Cross-Site Scripting (XSS) vulnerabilities, demonstrates exploit examples, and provides fixes using `textContent` and DOMPurify. I identify three distinct vulnerability classes and explain their root causes.

## Vulnerabilities Identified

### 1. Stored XSS — Guestbook entries via localStorage

**Location**: `vulnerable.html` — `loadEntries()` function, innerHTML concatenation.

The application reads stored guestbook entries from localStorage and renders them by appending to `innerHTML`. Because the stored data (name and message) is user-controlled, an attacker can inject a malicious script that persists across page reloads.

**Exploit example:**
```
Name: <img src=x onerror=alert(document.cookie)>
Message: <b>innocent</b>
```
When any user visits the guestbook page, the `<img>` tag fires `onerror` and executes JavaScript in their session context.

**Root cause**: `container.innerHTML += '<li>...' + e.msg + '</li>'` — user data is interpolated into an HTML string without escaping.

**Fix**: Use `textContent` and `document.createElement()` instead of `innerHTML`:
```js
const li = document.createElement('li');
const strong = document.createElement('strong');
strong.textContent = e.name;
li.appendChild(strong);
li.appendChild(document.createTextNode(': ' + e.msg));
container.appendChild(li);
```

### 2. Reflected XSS — URL query parameter

**Location**: `vulnerable.html` — `welcome.innerHTML` from `?name=` parameter.

The `name` query parameter is read from the URL and written directly into `innerHTML`. An attacker crafts a link:
```
guestbook.html?name=<img src=x onerror=alert('Reflected XSS')>
```
When a victim clicks the link, the script executes immediately.

**Root cause**: `document.getElementById('welcome').innerHTML = 'Welcome, ' + userName + '!'`

**Fix**: Use `textContent` which automatically escapes HTML entities:
```js
document.getElementById('welcome').textContent = 'Welcome, ' + userName + '!';
```

### 3. DOM-Based XSS — URL hash fragment

**Location**: `vulnerable.html` — `location.hash` written to `innerHTML`.

The URL fragment (`#...`) is read via `location.hash` and inserted as raw HTML. The hash is never sent to the server, making this purely client-side DOM-based XSS.

**Exploit example:**
```
guestbook.html#<img src=x onerror=alert('DOM-XSS')>
```

**Root cause**: `note.innerHTML = 'Hash note: ' + hash` — `hash` is attacker-controlled via the URL fragment.

**Fix options:**
1. **Preferred**: Use `textContent` when the output is plain text.
2. **DOMPurify**: When HTML is legitimately needed, sanitize first:
```js
note.innerHTML = 'Hash note: ' + DOMPurify.sanitize(hash);
```

## Edge Cases Considered

| Edge Case | risk | Mitigation |
|-----------|------|------------|
| Empty name/message | Low — no injection, but UX concern | Validate on submit |
| Very long payload (10K+ chars) | Low — truncation in UI | CSS `max-width` + overflow |
| Nested HTML in stored data | **High** — stored XSS | textContent strips all tags |
| URL hash with `#` only | Low — empty string | Falsy check `if (hash)` |
| Malformed DOMPurify bypass | Varies | Keep library updated + combine with CSP |
| Mixed HTML + plain text | Medium — partial rendering | Whitelist or split text nodes |
| Multiple concurrent entries | Low — race condition | Async handling not needed (sync localStorage) |
| Script in `localStorage` key | Low — `getItem()` returns string | Safe by API design |

## Concise Mitigation Checklist

1. **Never use innerHTML** with user-controlled input — always prefer `textContent` or `createTextNode`.
2. **When HTML is required** (rich text), use DOMPurify (`DOMPurify.sanitize()`) before `innerHTML`.
3. **Validate and encode** all URL parameters (search, hash) before rendering.
4. **Use Content Security Policy** as a defense-in-depth layer.
5. **Avoid `eval()`** and `setTimeout(string)` — use event-driven patterns.
6. **Sanitize on write AND escape on read** for stored data.

## Files in Solution

| File | Description |
|------|-------------|
| `vulnerable.html` | Original template with 3 XSS vulnerabilities |
| `fixed.html` | Patched version using textContent + DOMPurify |
| `solution.md` | This report — analysis, exploits, and fixes |
