"""Pytest fixtures for T01 bug fixing tests."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Provide a TestClient for the main app."""
    from main import app, service
    # Reset state before each test
    service._users.clear()
    with TestClient(app) as c:
        yield c
