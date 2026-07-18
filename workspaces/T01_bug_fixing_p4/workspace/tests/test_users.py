"""
Tests verifying the three bug fixes in the user service.

BUG-1: GET /users/{id} returns 404 instead of crashing with None
BUG-2: POST /users rejects empty names
BUG-3: PUT /users/{id} returns 404 when user doesn't exist
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app, db


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory DB before every test."""
    db._users.clear()
    db._next_id = 1
    yield


client = TestClient(app)


# ── BUG-1: GET /users/{id} returns 404 (not None / crash) ──────────────

class TestGetUser:
    def test_get_existing_user_returns_user(self):
        created = client.post("/users", json={"name": "Alice"}).json()
        resp = client.get(f"/users/{created['id']}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "Alice"

    def test_get_nonexistent_user_returns_404(self):
        """BUG-1: Must return 404, not crash with None."""
        resp = client.get("/users/999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_user_detail_is_informative(self):
        resp = client.get("/users/999")
        assert "detail" in resp.json()
        assert "not found" in resp.json()["detail"].lower()


# ── BUG-2: POST /users rejects empty names ─────────────────────────────

class TestCreateUser:
    def test_create_valid_user(self):
        resp = client.post("/users", json={"name": "Bob"})
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["name"] == "Bob"
        assert data["id"] == 1

    def test_create_user_without_name_field(self):
        resp = client.post("/users", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_user_with_empty_name_string(self):
        """BUG-2: Empty string name must be rejected."""
        resp = client.post("/users", json={"name": ""})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_user_with_none_name(self):
        """None name must be rejected."""
        resp = client.post("/users", json={"name": None})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_returns_201_status(self):
        resp = client.post("/users", json={"name": "Charlie"})
        assert resp.status_code == status.HTTP_201_CREATED


# ── BUG-3: PUT /users/{id} checks existence before updating ────────────

class TestUpdateUser:
    def test_update_existing_user(self):
        created = client.post("/users", json={"name": "Diana"}).json()
        resp = client.put(f"/users/{created['id']}", json={"name": "Diana Updated"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "Diana Updated"

    def test_update_nonexistent_user_returns_404(self):
        """BUG-3: Must return 404, not silently fail or crash."""
        resp = client.put("/users/777", json={"name": "Ghost"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_preserves_other_fields(self):
        created = client.post("/users", json={"name": "Frank"}).json()
        resp = client.put(f"/users/{created['id']}", json={"name": "Frankie"})
        assert resp.json()["id"] == created["id"]

    def test_update_with_empty_name_rejected(self):
        created = client.post("/users", json={"name": "Grace"}).json()
        resp = client.put(f"/users/{created['id']}", json={"name": ""})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_existing_user_detail_on_404(self):
        resp = client.put("/users/0", json={"name": "No one"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in resp.json()


# ── Integration: happy path flow ───────────────────────────────────────

class TestUserFlow:
    def test_full_crud_flow(self):
        # Create
        r1 = client.post("/users", json={"name": "Isaac"})
        assert r1.status_code == 201
        uid = r1.json()["id"]

        # Read
        r2 = client.get(f"/users/{uid}")
        assert r2.status_code == 200
        assert r2.json()["name"] == "Isaac"

        # Update
        r3 = client.put(f"/users/{uid}", json={"name": "Isaac Newton"})
        assert r3.status_code == 200
        assert r3.json()["name"] == "Isaac Newton"

        # List
        r4 = client.get("/users")
        assert r4.status_code == 200
        assert len(r4.json()) == 1

        # Delete
        r5 = client.delete(f"/users/{uid}")
        assert r5.status_code == 204

        # Confirm gone
        r6 = client.get(f"/users/{uid}")
        assert r6.status_code == 404

    def test_multiple_users(self):
        ids = []
        for name in ["A", "B", "C"]:
            r = client.post("/users", json={"name": name})
            ids.append(r.json()["id"])
        all_users = client.get("/users").json()
        assert len(all_users) == 3

        # Each individual get works
        for uid in ids:
            resp = client.get(f"/users/{uid}")
            assert resp.status_code == 200

        # Missing user after all that still 404
        assert client.get("/users/999").status_code == 404
