"""Tests for User CRUD API (synchronous, using conftest's client fixture)."""
import pytest
from main import users_db
import main as m


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory DB before each test."""
    users_db.clear()
    m.next_id = 1
    yield


# --- CREATE ---

def test_create_user_201(client):
    resp = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["age"] == 30
    assert "created_at" in data
    assert "updated_at" in data


def test_create_user_invalid_email_422(client):
    resp = client.post("/users", json={
        "name": "Alice",
        "email": "not-an-email",
        "age": 30,
    })
    assert resp.status_code == 422


def test_create_user_name_too_short_422(client):
    resp = client.post("/users", json={
        "name": "Al",
        "email": "alice@example.com",
        "age": 30,
    })
    assert resp.status_code == 422


def test_create_user_age_zero_422(client):
    resp = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 0,
    })
    assert resp.status_code == 422


def test_create_user_age_negative_422(client):
    resp = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com",
        "age": -5,
    })
    assert resp.status_code == 422


# --- LIST ---

def test_list_users_empty_200(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_users_200(client):
    # Create a user first
    client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice"


# --- GET BY ID ---

def test_get_user_200(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


def test_get_user_not_found_404(client):
    resp = client.get("/users/999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# --- UPDATE ---

def test_update_user_200(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.put(f"/users/{user_id}", json={
        "name": "Alice Updated",
        "age": 31,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Alice Updated"
    assert data["age"] == 31
    assert data["email"] == "alice@example.com"  # unchanged


def test_update_user_not_found_404(client):
    resp = client.put("/users/999", json={"name": "Nobody"})
    assert resp.status_code == 404


def test_update_user_invalid_email_422(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.put(f"/users/{user_id}", json={
        "email": "bad-email",
    })
    assert resp.status_code == 422


def test_update_user_no_fields_400(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.put(f"/users/{user_id}", json={})
    assert resp.status_code == 400


# --- DELETE ---

def test_delete_user_204(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 204
    # Verify it's gone
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404


def test_delete_user_not_found_404(client):
    resp = client.delete("/users/999")
    assert resp.status_code == 404


# --- AUTO-INCREMENT ---

def test_id_auto_increment(client):
    u1 = client.post("/users", json={"name": "User1", "email": "u1@test.com", "age": 20})
    u2 = client.post("/users", json={"name": "User2", "email": "u2@test.com", "age": 25})
    assert u1.json()["id"] == 1
    assert u2.json()["id"] == 2


# --- PARTIAL UPDATE ---

def test_update_user_partial_name_only(client):
    create_resp = client.post("/users", json={
        "name": "Alice", "email": "alice@example.com", "age": 30,
    })
    user_id = create_resp.json()["id"]
    resp = client.put(f"/users/{user_id}", json={"name": "Bob"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Bob"
    assert data["email"] == "alice@example.com"
    assert data["age"] == 30
