"""Pytest fixtures for the user-service test suite."""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Provide a TestClient instance wrapping the FastAPI app."""
    with TestClient(app) as c:
        yield c
