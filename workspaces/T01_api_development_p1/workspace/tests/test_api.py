"""Tests for the User CRUD API (T01_api_development)."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_db():
    """Reset the in-memory store before every test."""
    import main as m
    m._db.clear()
    yield


# ===================================================================
# POST /users  —  CREATE
# ===================================================================

class TestCreateUser:
    def test_create_valid_user(self, client: TestClient):
        resp = client.post("/users", json={
            "name": "Bob", "email": "bob@example.com", "age": 25,
        })
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["name"] == "Bob"
        assert data["email"] == "bob@example.com"
        assert data["age"] == 25
        assert "id" in data
        assert len(data["id"]) == 36  # UUID length

    def test_create_returns_201(self, client: TestClient):
        resp = client.post("/users", json={
            "name": "Carol", "email": "carol@x.com", "age": 20,
        })
        assert resp.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize("payload", [
        {"name": "A", "email": "a@b.com", "age": 10},          # name too short
        {"name": "  X  ", "email": "x@y.com", "age": 10},      # stripped name too short
        {"name": "Valid", "email": "not-an-email", "age": 10}, # bad email
        {"name": "Valid", "email": "a@b.com", "age": 0},       # age == 0
        {"name": "Valid", "email": "a@b.com", "age": -5},      # age < 0
    ])
    def test_validation_errors(self, client: TestClient, payload):
        resp = client.post("/users", json=payload)
        assert resp.status_code == 422

    def test_empty_name_rejected(self, client: TestClient):
        resp = client.post("/users", json={
            "name": "", "email": "a@b.com", "age": 10,
        })
        assert resp.status_code == 422

    def test_missing_field(self, client: TestClient):
        resp = client.post("/users", json={"name": "Alice"})
        assert resp.status_code == 422

    def test_age_not_int(self, client: TestClient):
        resp = client.post("/users", json={
            "name": "Valid", "email": "a@b.com", "age": "abc",
        })
        assert resp.status_code == 422


# ===================================================================
# GET /users  —  LIST
# ===================================================================

class TestListUsers:
    def test_empty_list(self, client: TestClient):
        resp = client.get("/users")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_list_after_creation(self, client: TestClient):
        client.post("/users", json={
            "name": "Alice", "email": "alice@x.com", "age": 30,
        })
        resp = client.get("/users")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    def test_list_multiple(self, client: TestClient):
        for i in range(5):
            client.post("/users", json={
                "name": f"User{i}", "email": f"u{i}@x.com", "age": 20 + i,
            })
        resp = client.get("/users")
        assert len(resp.json()) == 5

    def test_list_returns_200(self, client: TestClient):
        resp = client.get("/users")
        assert resp.status_code == status.HTTP_200_OK

    def test_list_returns_array(self, client: TestClient):
        resp = client.get("/users")
        assert isinstance(resp.json(), list)


# ===================================================================
# GET /users/{id}  —  GET BY ID
# ===================================================================

class TestGetUser:
    def _create_user(self, client: TestClient, name="Alice", email="alice@x.com", age=30):
        return client.post("/users", json={
            "name": name, "email": email, "age": age,
        }).json()

    def test_get_existing(self, client: TestClient):
        user = self._create_user(client)
        uid = user["id"]
        resp = client.get(f"/users/{uid}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "Alice"

    def test_get_nonexistent(self, client: TestClient):
        resp = client.get("/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_get_returns_200(self, client: TestClient):
        user = self._create_user(client)
        resp = client.get(f"/users/{user['id']}")
        assert resp.status_code == status.HTTP_200_OK

    def test_get_returns_correct_user(self, client: TestClient):
        self._create_user(client, name="Alice")
        u2 = self._create_user(client, name="Bob")
        resp = client.get(f"/users/{u2['id']}")
        assert resp.json()["name"] == "Bob"


# ===================================================================
# PUT /users/{id}  —  UPDATE
# ===================================================================

class TestUpdateUser:
    def _create_user(self, client: TestClient):
        return client.post("/users", json={
            "name": "Alice", "email": "alice@x.com", "age": 30,
        }).json()

    def test_update_all_fields(self, client: TestClient):
        user = self._create_user(client)
        uid = user["id"]
        resp = client.put(f"/users/{uid}", json={
            "name": "Alice Updated", "email": "alice.new@x.com", "age": 31,
        })
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["name"] == "Alice Updated"
        assert data["email"] == "alice.new@x.com"
        assert data["age"] == 31

    def test_update_partial(self, client: TestClient):
        user = self._create_user(client)
        uid = user["id"]
        resp = client.put(f"/users/{uid}", json={"age": 99})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["age"] == 99
        assert resp.json()["name"] == "Alice"  # unchanged

    def test_update_nonexistent(self, client: TestClient):
        resp = client.put("/users/00000000-0000-0000-0000-000000000000", json={"name": "ValidName"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_validation_error(self, client: TestClient):
        user = self._create_user(client)
        resp = client.put(f"/users/{user['id']}", json={"age": -1})
        assert resp.status_code == 422

    def test_update_preserves_unchanged_fields(self, client: TestClient):
        user = self._create_user(client)
        client.put(f"/users/{user['id']}", json={"name": "NewName"})
        resp = client.get(f"/users/{user['id']}")
        assert resp.json()["email"] == "alice@x.com"
        assert resp.json()["age"] == 30


# ===================================================================
# DELETE /users/{id}  —  DELETE
# ===================================================================

class TestDeleteUser:
    def _create_user(self, client: TestClient):
        return client.post("/users", json={
            "name": "Alice", "email": "alice@x.com", "age": 30,
        }).json()

    def test_delete_existing(self, client: TestClient):
        user = self._create_user(client)
        uid = user["id"]
        resp = client.delete(f"/users/{uid}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        # verify gone
        get_resp = client.get(f"/users/{uid}")
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_still_204(self, client: TestClient):
        resp = client.delete("/users/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_list_after_delete(self, client: TestClient):
        user = self._create_user(client)
        client.delete(f"/users/{user['id']}")
        resp = client.get("/users")
        assert resp.json() == []


# ===================================================================
# Full lifecycle
# ===================================================================

class TestLifecycle:
    def test_create_read_update_delete(self, client: TestClient):
        # Create
        created = client.post("/users", json={
            "name": "Diana", "email": "diana@x.com", "age": 28,
        }).json()
        uid = created["id"]

        # Read
        got = client.get(f"/users/{uid}").json()
        assert got["name"] == "Diana"

        # Update
        client.put(f"/users/{uid}", json={"age": 29})
        updated = client.get(f"/users/{uid}").json()
        assert updated["age"] == 29

        # Delete
        client.delete(f"/users/{uid}")
        assert client.get(f"/users/{uid}").status_code == status.HTTP_404_NOT_FOUND
