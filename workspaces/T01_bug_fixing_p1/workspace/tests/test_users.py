"""Tests for the User Service — covers all three bug fixes."""
import pytest
from fastapi.testclient import TestClient

from main import app, reset_store


@pytest.fixture(autouse=True)
def clean_store():
    """Reset the in-memory store before every test."""
    reset_store()


client = TestClient(app)


# ─── Bug #1: GET /users/{id} crashes when user not found ───────────────────

class TestGetUserNotFound:
    """Bug #1: returns 404 instead of 500 when user does not exist."""

    def test_returns_404_for_missing_user(self):
        resp = client.get("/users/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_returns_404_for_zero(self):
        resp = client.get("/users/0")
        assert resp.status_code == 404

    def test_returns_404_for_negative_id(self):
        resp = client.get("/users/-1")
        assert resp.status_code == 404

    def test_existing_user_returns_200(self):
        create_resp = client.post("/users", json={"name": "Alice"})
        uid = create_resp.json()["id"]
        resp = client.get(f"/users/{uid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice"


# ─── Bug #2: POST /users accepts empty names ───────────────────────────────

class TestCreateUserEmptyName:
    """Bug #2: rejects empty / whitespace-only names with 422."""

    def test_rejects_empty_string_name(self):
        resp = client.post("/users", json={"name": ""})
        assert resp.status_code == 422

    def test_rejects_whitespace_only_name(self):
        resp = client.post("/users", json={"name": "   "})
        assert resp.status_code == 422

    def test_accepts_valid_name(self):
        resp = client.post("/users", json={"name": "Bob"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Bob"

    def test_trims_whitespace(self):
        resp = client.post("/users", json={"name": "  Charlie  "})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Charlie"

    def test_rejects_missing_name_field(self):
        resp = client.post("/users", json={})
        assert resp.status_code == 422


# ─── Bug #3: PUT /users/{id} doesn't check if user exists ──────────────────

class TestUpdateUserNotFound:
    """Bug #3: returns 404 when updating a non-existent user."""

    def test_returns_404_for_missing_user(self):
        resp = client.put("/users/999", json={"name": "Nobody"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_updates_existing_user(self):
        create_resp = client.post("/users", json={"name": "Dave"})
        uid = create_resp.json()["id"]
        resp = client.put(f"/users/{uid}", json={"name": "Dave Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Dave Updated"
        get_resp = client.get(f"/users/{uid}")
        assert get_resp.json()["name"] == "Dave Updated"

    def test_rejects_empty_name_on_update(self):
        create_resp = client.post("/users", json={"name": "Eve"})
        uid = create_resp.json()["id"]
        resp = client.put(f"/users/{uid}", json={"name": ""})
        assert resp.status_code == 422
