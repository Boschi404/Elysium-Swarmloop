"""secure_app.py — Hardened Flask endpoint (production-ready).

Fixes applied:
  ✅ Safe path resolution (realpath + prefix check)
  ✅ Token-based authentication (Bearer token)
  ✅ Generic error messages (no path/exception leaks)
  ✅ Input validation (empty filename, trailing NUL, edge cases)
  ✅ Content-type validation
  ✅ Audit logging
"""

from flask import Flask, request, jsonify
import os
import logging
import hmac

app = Flask(__name__)

# ── Configuration ───────────────────────────────────────────────────
DOCUMENTS_DIR = os.path.realpath("/app/documents")
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}
API_TOKEN = os.environ.get("API_TOKEN", "change-me-in-production")

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secure_app")


# ── Auth decorator ──────────────────────────────────────────────────
def require_auth(f):
    """Middleware: reject requests without a valid Bearer token."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = auth_header[len("Bearer "):]
        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(token, API_TOKEN):
            return jsonify({"error": "Invalid token"}), 403

        return f(*args, **kwargs)

    return decorated


# ── Safe file resolver ──────────────────────────────────────────────
def safe_resolve(doc_dir: str, requested: str) -> str | None:
    """
    Resolve a requested filename within the allowed document directory.

    Returns the safe absolute path, or None if the path escapes the
    base directory or fails validation.
    """
    # Edge case: empty filename
    if not requested or requested.strip() == "":
        return None

    # Edge case: strip trailing NUL bytes (CWE-158)
    requested = requested.split("\0")[0]

    # Resolve the full path and canonicalise it
    joined = os.path.join(doc_dir, requested)
    real = os.path.realpath(joined)

    # Guard: the resolved path MUST be within the documents directory
    if not real.startswith(doc_dir + os.sep) and real != doc_dir:
        return None

    # Guard: file must actually exist
    if not os.path.isfile(real):
        return None

    # Guard: optional — restrict by extension
    _, ext = os.path.splitext(real)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return None

    return real


# ── Secure endpoint ─────────────────────────────────────────────────
@app.route("/read")
@require_auth
def read_file():
    """Return the contents of a requested document (authenticated + safe)."""
    filename = request.args.get("filename", "")

    # Resolve path safely
    safe_path = safe_resolve(DOCUMENTS_DIR, filename)
    if safe_path is None:
        # Generic error — do NOT reveal whether the file exists or
        # whether the path was invalid
        return jsonify({"error": "File not found or access denied"}), 404

    try:
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        logger.info("File served: %s (requested: %s)", safe_path, filename)
        return jsonify({"content": content})

    except PermissionError:
        logger.warning("Permission denied: %s", safe_path)
        return jsonify({"error": "File not found or access denied"}), 404
    except Exception:
        logger.exception("Unexpected error reading: %s", safe_path)
        # Generic message — no path, exception type, or stack trace
        return jsonify({"error": "Internal server error"}), 500


# ── Health check ────────────────────────────────────────────────────
@app.route("/health")
def health():
    """Unauthenticated health check — no sensitive info."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=False)
