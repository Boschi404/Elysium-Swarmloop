"""
Tests for the User CRUD API.
Uses FastAPI TestClient for in-process testing.
"""

from fastapi.testclient import TestClient
import pytest

from main import app

client = TestClient(app)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_store():
    """Reset the in-memory store before each test."""
    from main import _db, _next_id
    _db.clear()
    # Reset _next_id via assignment since it's a module-level int
    import main as _m
    _m._next_id = 1
    yield


def _create_test_user(name="Alice", email="alice@example.com", age=30):
    return client.post("/users", json={
        "name": name,
        "email": email,
        "age": age,
    })


# ── POST /users ─────────────────────────────────────────────────────────────

class TestCreateUser:
    def test_create_user_returns_201(self):
        resp = _create_test_user()
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert data["name"] == "Alice"
        assert data["email"] == "alice@example.com"
        assert data["age"] == 30

    def test_create_user_increments_id(self):
        u1 = _create_test_user(name="Alice")
        u2 = _create_test_user(name="Bob")
        assert u1.json()["id"] == 1
        assert u2.json()["id"] == 2

    def test_create_user_name_too_short(self):
        resp = client.post("/users", json={
            "name": "Ab",
            "email": "b@b.com",
            "age": 20,
        })
        assert resp.status_code == 422

    def test_create_user_invalid_email(self):
        resp = client.post("/users", json={
            "name": "Bob",
            "email": "not-an-email",
            "age": 20,
        })
        assert resp.status_code == 422

    def test_create_user_age_zero(self):
        resp = client.post("/users", json={
            "name": "Bob",
            "email": "bob@b.com",
            "age": 0,
        })
        assert resp.status_code == 422

    def test_create_user_age_negative(self):
        resp = client.post("/users", json={
            "name": "Bob",
            "email": "bob@b.com",
            "age": -5,
        })
        assert resp.status_code == 422

    def test_create_user_missing_fields(self):
        resp = client.post("/users", json={"name": "Bob"})
        assert resp.status_code == 422


# ── GET /users ──────────────────────────────────────────────────────────────

class TestListUsers:
    def test_list_empty(self):
        resp = client.get("/users")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_one_user(self):
        _create_test_user()
        resp = client.get("/users")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    def test_list_multiple_users(self):
        _create_test_user(name="Alice")
        _create_test_user(name="Bob")
        _create_test_user(name="Carol")
        resp = client.get("/users")
        assert resp.status_code == 200
        assert len(resp.json()) == 3


# ── GET /users/{id} ────────────────────────────────────────────────────────

class TestGetUser:
    def test_get_existing_user(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.get(f"/users/{uid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice"

    def test_get_nonexistent_user(self):
        resp = client.get("/users/999")
        assert resp.status_code == 404

    def test_get_after_delete(self):
        created = _create_test_user()
        uid = created.json()["id"]
        client.delete(f"/users/{uid}")
        resp = client.get(f"/users/{uid}")
        assert resp.status_code == 404


# ── PUT /users/{id} ────────────────────────────────────────────────────────

class TestUpdateUser:
    def test_update_all_fields(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.put(f"/users/{uid}", json={
            "name": "Alice Updated",
            "email": "alice.new@example.com",
            "age": 31,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Alice Updated"
        assert data["email"] == "alice.new@example.com"
        assert data["age"] == 31
        assert data["id"] == uid  # id unchanged

    def test_update_partial(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.put(f"/users/{uid}", json={"age": 99})
        assert resp.status_code == 200
        data = resp.json()
        assert data["age"] == 99
        assert data["name"] == "Alice"  # unchanged

    def test_update_nonexistent(self):
        resp = client.put("/users/999", json={"name": "Ghost"})
        assert resp.status_code == 404

    def test_update_empty_body(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.put(f"/users/{uid}", json={})
        assert resp.status_code == 400

    def test_update_invalid_name(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.put(f"/users/{uid}", json={"name": "X"})
        assert resp.status_code == 422

    def test_update_invalid_age(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.put(f"/users/{uid}", json={"age": 0})
        assert resp.status_code == 422


# ── DELETE /users/{id} ──────────────────────────────────────────────────────

class TestDeleteUser:
    def test_delete_existing(self):
        created = _create_test_user()
        uid = created.json()["id"]
        resp = client.delete(f"/users/{uid}")
        assert resp.status_code == 204
        # Verify it's gone
        assert client.get(f"/users/{uid}").status_code == 404

    def test_delete_nonexistent(self):
        resp = client.delete("/users/999")
        assert resp.status_code == 404

    def test_delete_then_list_empty(self):
        created = _create_test_user()
        uid = created.json()["id"]
        client.delete(f"/users/{uid}")
        resp = client.get("/users")
        assert resp.json() == []
