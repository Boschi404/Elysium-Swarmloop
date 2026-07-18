"""
Tests for User Service — verifying all three bug fixes.
"""

import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


# ── Helpers ──────────────────────────────────────────────────────────

def reset_db():
    main.users_db.clear()
    main.users_db[1] = {"id": 1, "name": "Alice"}
    main.users_db[2] = {"id": 2, "name": "Bob"}
    main.next_id = 3


# ── Bug 1: GET /users/{id} when user not found ─────────────────────

class TestGetUser:
    def setup_method(self):
        reset_db()

    def test_get_existing_user(self):
        """Existing user returns 200 and the user object."""
        resp = client.get("/users/1")
        assert resp.status_code == 200
        assert resp.json() == {"id": 1, "name": "Alice"}

    def test_get_nonexistent_user_returns_404(self):
        """BUG 1 fix: missing user → 404, not None crash."""
        resp = client.get("/users/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"


# ── Bug 2: POST /users with empty names ──────────────────────────

class TestCreateUser:
    def setup_method(self):
        reset_db()

    def test_create_valid_user(self):
        """Valid user is created with 201."""
        resp = client.post("/users", json={"name": "Charlie"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Charlie"
        assert data["id"] == 3  # next available

    def test_create_user_with_empty_name_rejected(self):
        """BUG 2 fix: empty name string → 422."""
        resp = client.post("/users", json={"name": ""})
        assert resp.status_code == 422

    def test_create_user_with_whitespace_only_name_rejected(self):
        """BUG 2 fix: whitespace-only name → 422."""
        resp = client.post("/users", json={"name": "   "})
        assert resp.status_code == 422

    def test_create_user_with_missing_name_field(self):
        """Missing name key → 422 (Pydantic validation)."""
        resp = client.post("/users", json={})
        assert resp.status_code == 422


# ── Bug 3: PUT /users/{id} without existence check ─────────────────

class TestUpdateUser:
    def setup_method(self):
        reset_db()

    def test_update_existing_user(self):
        """Updating an existing user succeeds."""
        resp = client.put("/users/1", json={"name": "Alicia"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alicia"

    def test_update_nonexistent_user_returns_404(self):
        """BUG 3 fix: updating a missing user → 404."""
        resp = client.put("/users/999", json={"name": "Ghost"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_update_partial_no_name(self):
        """PUT with only name=None keeps the original name."""
        resp = client.put("/users/1", json={})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice"  # unchanged

    def test_update_with_empty_name_rejected(self):
        """PUT with empty name → 422."""
        resp = client.put("/users/1", json={"name": ""})
        assert resp.status_code == 422

    def test_update_with_whitespace_name_rejected(self):
        """PUT with whitespace-only name → 422."""
        resp = client.put("/users/1", json={"name": "   "})
        assert resp.status_code == 422


# ── Edge cases ───────────────────────────────────────────────────────

class TestDeleteUser:
    def setup_method(self):
        reset_db()

    def test_delete_existing_user(self):
        resp = client.delete("/users/1")
        assert resp.status_code == 204

    def test_delete_nonexistent_user(self):
        resp = client.delete("/users/999")
        assert resp.status_code == 404

    def test_get_deleted_user_returns_404(self):
        client.delete("/users/2")
        resp = client.get("/users/2")
        assert resp.status_code == 404
