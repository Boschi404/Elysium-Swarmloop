"""
User Service Module — re-exports from main.

Kept for backward compatibility with tests that import user_service directly.
"""

from main import app, users_db  # noqa: F401
