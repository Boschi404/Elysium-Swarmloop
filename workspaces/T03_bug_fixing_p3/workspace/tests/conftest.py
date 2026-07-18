"""Shared pytest fixtures for all test files."""

import os
import sys
import tempfile

import pytest

# Ensure workspace is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app, init_db, DATABASE


@pytest.fixture
def client():
    """Create a test client with a temporary database."""
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(tmp_fd)

    app.config["TESTING"] = True

    import main as app_module

    original_db = app_module.DATABASE
    app_module.DATABASE = tmp_path

    init_db()

    with app.test_client() as c:
        yield c

    app_module.DATABASE = original_db
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
