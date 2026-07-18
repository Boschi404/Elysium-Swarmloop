"""Pytest fixtures for the User Service tests."""
import pytest
from fastapi.testclient import TestClient
from main import app, reset_store


@pytest.fixture
def client():
    """FastAPI TestClient with a clean store before every test."""
    reset_store()
    with TestClient(app) as c:
        yield c
