"""vuln_app.py — VULNERABLE Flask endpoint (DO NOT USE IN PRODUCTION).

This file demonstrates three critical security vulnerabilities:
  1. Path traversal (arbitrary file read)
  2. Missing authentication
  3. Verbose error messages leaking internal information
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# "Secure" documents directory
DOCUMENTS_DIR = "/app/documents"


@app.route("/read")
def read_file():
    """VULNERABLE: reads a file by name from GET param, no auth, no path check."""
    filename = request.args.get("filename", "")
    filepath = os.path.join(DOCUMENTS_DIR, filename)

    try:
        with open(filepath, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        # VULNERABILITY #3: full traceback leaks internal paths and Python version
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
