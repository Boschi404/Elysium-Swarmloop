#!/usr/bin/env python3
"""
Tests for T02_security_analysis — XSS Vulnerability Review.

Validates:
  1. Solution report (solution.md) meets rubric criteria
  2. Vulnerable HTML template exists and contains XSS patterns
  3. Fixed HTML template exists and uses safe APIs
"""

import sys
import os
import re
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ──────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────
WORKSPACE = os.path.join(os.path.dirname(__file__), "..")
SOLUTION_MD = os.path.join(WORKSPACE, "solution.md")
VULNERABLE_HTML = os.path.join(WORKSPACE, "vulnerable.html")
FIXED_HTML = os.path.join(WORKSPACE, "fixed.html")


def _read_solution_md():
    with open(SOLUTION_MD, "r", encoding="utf-8") as f:
        return f.read()


def _read_vulnerable_html():
    with open(VULNERABLE_HTML, "r", encoding="utf-8") as f:
        return f.read()


def _read_fixed_html():
    with open(FIXED_HTML, "r", encoding="utf-8") as f:
        return f.read()


# ──────────────────────────────────────────────────────────────
# File existence
# ──────────────────────────────────────────────────────────────
def test_solution_md_exists():
    assert os.path.isfile(SOLUTION_MD), f"Missing: {SOLUTION_MD}"


def test_vulnerable_html_exists():
    assert os.path.isfile(VULNERABLE_HTML), f"Missing: {VULNERABLE_HTML}"


def test_fixed_html_exists():
    assert os.path.isfile(FIXED_HTML), f"Missing: {FIXED_HTML}"


# ──────────────────────────────────────────────────────────────
# Rubric: Correctness (40%)
# ──────────────────────────────────────────────────────────────
def test_rubric_correctness():
    """Rubric: contains 'solution', min_length 100, regex xss|vulnerability|review"""
    text = _read_solution_md()
    assert "solution" in text.lower(), "Missing 'solution'"
    assert len(text) >= 100, f"Too short: {len(text)} chars"
    assert re.search(r"xss|vulnerability|review", text, re.IGNORECASE), \
        "Missing required regex (xss|vulnerability|review)"


# ──────────────────────────────────────────────────────────────
# Rubric: Completeness (25%)
# ──────────────────────────────────────────────────────────────
def test_rubric_completeness():
    """Rubric: contains 'identify', 'explain', min_length 200"""
    text = _read_solution_md()
    assert "identify" in text.lower(), "Missing 'identify'"
    assert "explain" in text.lower(), "Missing 'explain'"
    assert len(text) >= 200, f"Too short: {len(text)} chars"


# ──────────────────────────────────────────────────────────────
# Rubric: Efficiency (15%)
# ──────────────────────────────────────────────────────────────
def test_rubric_efficiency():
    """Rubric: contains 'concise', min_length 50"""
    text = _read_solution_md()
    assert "concise" in text.lower(), "Missing 'concise'"
    assert len(text) >= 50, f"Too short: {len(text)} chars"


# ──────────────────────────────────────────────────────────────
# Rubric: Robustness (10%)
# ──────────────────────────────────────────────────────────────
def test_rubric_robustness():
    """Rubric: contains 'edge case', 'example'"""
    text = _read_solution_md()
    assert "edge case" in text.lower(), "Missing 'edge case'"
    assert "example" in text.lower(), "Missing 'example'"


# ──────────────────────────────────────────────────────────────
# Rubric: Clarity (10%)
# ──────────────────────────────────────────────────────────────
def test_rubric_clarity():
    """Rubric: has '#' structure, min_length 150"""
    text = _read_solution_md()
    assert "# " in text, "Missing markdown heading structure (#)"
    assert text.count("# ") >= 2, "Need at least 2 headings"
    assert len(text) >= 150, f"Too short: {len(text)} chars"


# ──────────────────────────────────────────────────────────────
# Content: XSS vulnerability coverage
# ──────────────────────────────────────────────────────────────
def test_covers_stored_xss():
    """Solution must mention stored XSS"""
    text = _read_solution_md()
    assert re.search(r"stored[-\s]?xss|stored.*cross.?site", text, re.IGNORECASE), \
        "Missing stored XSS coverage"


def test_covers_reflected_xss():
    """Solution must mention reflected XSS"""
    text = _read_solution_md()
    assert re.search(r"reflected[-\s]?xss|reflected.*cross.?site", text, re.IGNORECASE), \
        "Missing reflected XSS coverage"


def test_covers_dom_xss():
    """Solution must mention DOM-based XSS"""
    text = _read_solution_md()
    assert re.search(r"dom[-\s]?based[-\s]?xss|dom[-\s]?xss", text, re.IGNORECASE), \
        "Missing DOM-based XSS coverage"


# ──────────────────────────────────────────────────────────────
# Content: Fix coverage
# ──────────────────────────────────────────────────────────────
def test_mentions_textcontent():
    """Solution must mention textContent fix"""
    text = _read_solution_md()
    assert "textContent" in text or "textcontent" in text.lower(), \
        "Missing textContent fix"


def test_mentions_dompurify():
    """Solution must mention DOMPurify fix"""
    text = _read_solution_md()
    assert "DOMPurify" in text or "dompurify" in text.lower(), \
        "Missing DOMPurify fix"


# ──────────────────────────────────────────────────────────────
# Content: Vulnerable HTML has innerHTML
# ──────────────────────────────────────────────────────────────
def test_vulnerable_has_innerhtml():
    """Vulnerable template must use innerHTML (the root cause)"""
    html = _read_vulnerable_html()
    count = html.count("innerHTML")
    assert count >= 3, f"Expected 3+ innerHTML uses, found {count}"


# ──────────────────────────────────────────────────────────────
# Content: Fixed HTML uses textContent
# ──────────────────────────────────────────────────────────────
def test_fixed_uses_textcontent():
    """Fixed template must use textContent"""
    html = _read_fixed_html()
    assert "textContent" in html, "Missing textContent in fixed version"


def test_fixed_uses_dompurify():
    """Fixed template must reference DOMPurify"""
    html = _read_fixed_html()
    assert "DOMPurify" in html or "dompurify" in html.lower(), \
        "Missing DOMPurify in fixed version"


# ──────────────────────────────────────────────────────────────
# Content: Exploit examples
# ──────────────────────────────────────────────────────────────
def test_exploit_examples_present():
    """Solution must include exploit code examples"""
    text = _read_solution_md()
    assert "Exploit" in text or "exploit" in text.lower(), \
        "Missing exploit examples"


# ──────────────────────────────────────────────────────────────
# Run all if executed directly
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
