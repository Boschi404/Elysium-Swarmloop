"""Tests for the user service — verifying the three bug fixes."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app, users_db


client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _reset_store():
    """Reset the in-memory DB before every test so order doesn't matter."""
    users_db.clear()
    import main as svc
    svc.next_id = 1


def _create_user(name="Alice", email="alice@example.com") -> dict:
    resp = client.post("/users", json={"name": name, "email": email})
    assert resp.status_code == 201
    return resp.json()


# ===================================================================
# BUG 1 — GET /users/{id} crashes when user is not found
# ===================================================================
class TestGetUserNotFound:
    """The old code returned ``None`` for a missing id -> 500 crash."""

    def test_get_nonexistent_user_returns_404(self):
        """GET /users/42 should return 404, not crash."""
        resp = client.get("/users/42")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_get_after_delete_returns_404(self):
        """A user that was deleted should also 404."""
        user = _create_user()
        client.delete(f"/users/{user['id']}")
        resp = client.get(f"/users/{user['id']}")
        assert resp.status_code == 404

    def test_valid_user_still_works(self):
        """Existing users are returned normally (regression)."""
        user = _create_user(name="Bob")
        resp = client.get(f"/users/{user['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bob"


# ===================================================================
# BUG 2 — POST /users accepts empty names
# ===================================================================
class TestCreateUserEmptyName:
    """Fixed via Pydantic ``min_length=1`` on the name field."""

    def test_empty_string_name_returns_422(self):
        """Passing ``name=""`` should be rejected."""
        resp = client.post("/users", json={"name": "", "email": "x@y"})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_name_field_returns_422(self):
        """Omitting ``name`` entirely should also be rejected."""
        resp = client.post("/users", json={"email": "x@y"})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_null_name_returns_422(self):
        """Passing ``None`` as name should be rejected."""
        resp = client.post("/users", json={"name": None, "email": "x@y"})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ===================================================================
# BUG 3 — PUT /users/{id} doesn't check if user exists
# ===================================================================
class TestUpdateUserNotFound:
    """The old code tried to update a missing user and either crashed or
    silently did nothing."""

    def test_update_nonexistent_user_returns_404(self):
        """PUT /users/99 should return 404."""
        resp = client.put("/users/99", json={"name": "Ghost"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_update_without_name_field(self):
        """Partial update of a nonexistent user still returns 404."""
        resp = client.put("/users/1", json={"email": "new@x.com"})
        assert resp.status_code == 404

    def test_update_existing_user_works(self):
        """Updating an existing user succeeds (regression)."""
        user = _create_user(name="Charlie")
        resp = client.put(
            f"/users/{user['id']}", json={"name": "Charlie Updated"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Charlie Updated"

    def test_update_all_fields(self):
        """All updatable fields are persisted."""
        user = _create_user(name="Diana", email="d@o.com")
        resp = client.put(
            f"/users/{user['id']}",
            json={"name": "Diana New", "email": "d.new@o.com"},
        )
        data = resp.json()
        assert data["name"] == "Diana New"
        assert data["email"] == "d.new@o.com"

    def test_update_partial_email_only(self):
        """Partial update (only email) preserves the name."""
        user = _create_user(name="Eve", email="e@o.com")
        resp = client.put(
            f"/users/{user['id']}", json={"email": "eve@new.com"}
        )
        data = resp.json()
        assert data["name"] == "Eve"
        assert data["email"] == "eve@new.com"


# ===================================================================
# Integration — common workflows
# ===================================================================
class TestIntegration:
    """End-to-end scenarios combining the three fixes."""

    def test_full_lifecycle(self):
        """Create → read → update → read → delete → read (404)."""
        user = _create_user(name="Frank", email="f@x.com")
        uid = user["id"]

        resp = client.get(f"/users/{uid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Frank"

        resp = client.put(f"/users/{uid}", json={"name": "Frankie"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Frankie"

        resp = client.get(f"/users/{uid}")
        assert resp.json()["name"] == "Frankie"

        resp = client.delete(f"/users/{uid}")
        assert resp.status_code == 204

        resp = client.get(f"/users/{uid}")
        assert resp.status_code == 404

    def test_empty_list_when_no_users(self):
        """GET /users on an empty DB returns []."""
        resp = client.get("/users")
        assert resp.status_code == 200
        assert resp.json() == []
