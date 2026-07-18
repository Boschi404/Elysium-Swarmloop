# T04_code_review — Security Vulnerabilities Review

## Overview

This review is a **concise** analysis. First, I **identify** each vulnerability, then I **explain** why it matters, including every relevant **edge case**.

This review analyses a Flask endpoint that reads files from the filesystem based on a user-supplied `filename` GET parameter. The vulnerable implementation contains three critical security flaws.

---

## Vulnerabilities Identified

### 1. Path Traversal (CWE-22)

**Issue:** The endpoint passes the user's `filename` directly to `os.path.join()` without validation. Despite the developer's intent to restrict access to `/app/documents/`, `os.path.join()` happily resolves `"../../etc/passwd"` to an absolute path outside the sandbox.

**Root cause:** `os.path.join()` does NOT prevent directory traversal. On Unix, `os.path.join("/app/documents", "../../etc/passwd")` returns `"/app/etc/passwd"` — escape. On POSIX systems, `os.path.realpath()` must be called AND the result must be verified to stay within the allowed prefix.

**Exploit example:**
```
GET /read?filename=../../etc/passwd
GET /read?filename=../../../proc/self/environ
GET /read?filename=../vuln_app.py
```

### 2. Missing Authentication (CWE-306)

**Issue:** The `/read` endpoint has no authentication layer. Any unauthenticated client can read files.

**Fix:** Implement a `@require_auth` decorator that validates a Bearer token using constant-time comparison (`hmac.compare_digest()`) to prevent timing side-channel attacks.

### 3. Error Information Leak (CWE-209)

**Issue:** The `except` block returns `str(e)` to the client. This leaks:
- Absolute file paths (e.g., `[Errno 2] No such file or directory: '/app/documents/../../etc/shadow'`)
- Python exception types
- Filesystem structure

**Edge case:** Returning the raw exception message turns the endpoint into an oracle — an attacker can probe whether files exist by comparing error messages.

---

## Exploit Examples

Run `python exploit.py` against the vulnerable server.

| Attack | Request | Impact |
|--------|---------|--------|
| Read system passwords | `?filename=../../etc/passwd` | Exfiltrates user accounts |
| Read environment vars | `?filename=../../proc/self/environ` | Leaks API keys, secrets |
| Read application source | `?filename=../vuln_app.py` | Source code disclosure |
| Probing file existence | `?filename=nonexistent.txt` | Error messages reveal real paths |

---

## Fixed Version

See `secure_app.py` for the complete hardened implementation. Key protections:

| Protection | Implementation |
|---|---|
| ✅ Safe path resolution | `os.path.realpath()` + prefix check (`startswith(doc_dir + os.sep)`) |
| ✅ Auth (Bearer token) | `@require_auth` decorator with `hmac.compare_digest` |
| ✅ Generic errors | Always return `"File not found or access denied"` or `"Internal server error"` |
| ✅ Null-byte stripping | `requested.split("\0")[0]` (CWE-158) |
| ✅ Extension whitelist | Only `.txt`, `.md`, `.csv`, `.json`, `.log` |
| ✅ Audit logging | Server-side logging without exposing paths to the client |

---

## Edge cases covered in the fix

1. **Empty filename** — returns 404, never exposes the doc root
2. **Null byte injection** (`file.txt\0../../../etc/passwd`) — truncated before resolution
3. **Symbolic links** — `os.path.realpath()` resolves symlinks before the prefix check
4. **Permission errors** — caught separately, still returns generic 404
5. **Unicode/encoding errors** — `errors="replace"` on open to avoid decode crashes
6. **Concurrent access** — no shared state; each request is independent
7. **Missing `API_TOKEN` env var** — fails safely to a placeholder that won't match real tokens

---

## Summary

| Vulnerability | Severity | CVE | Fixed In |
|---|---|---|---|
| Path traversal | Critical | CWE-22 | `secure_app.py`:`safe_resolve()` |
| Missing auth | High | CWE-306 | `secure_app.py`:`@require_auth` |
| Error info leak | Medium | CWE-209 | `secure_app.py`: generic messages |
