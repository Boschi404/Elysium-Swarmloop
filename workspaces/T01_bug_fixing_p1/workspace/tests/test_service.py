"""
Tests for User Service — verifies all three bugs are fixed.

BUG 1: GET /users/{id} → 404 when user not found (not 500)
BUG 2: POST /users rejects empty/whitespace names → 422
BUG 3: PUT /users/{id} → 404 when updating non-existent user
"""

import pytest
from fastapi.testclient import TestClient
from main import app, service


@pytest.fixture(autouse=True)
def reset_service():
    """Reset the in-memory store before every test."""
    service._users.clear()
    yield


client = TestClient(app)


# ── Bug 1: GET /users/{id} on missing user ───────────────────────────────

def test_get_nonexistent_user_returns_404():
    """BUG 1: requesting a non-existent user must return 404, not crash."""
    response = client.get("/users/nonexistent-id")
    assert response.status_code == 404, (
        f"BUG 1: Expected 404 for missing user, got {response.status_code}. "
        f"Body: {response.text}"
    )
    assert "not found" in response.json().get("detail", "").lower()


def test_get_existing_user_succeeds():
    """Sanity check: existing user returns 200."""
    resp = client.post("/users", json={"name": "Alice"})
    uid = resp.json()["id"]

    response = client.get(f"/users/{uid}")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"


# ── Bug 2: POST /users rejects empty names ──────────────────────────────

def test_create_user_with_empty_name():
    """BUG 2: creating a user with empty name must be rejected (422)."""
    response = client.post("/users", json={"name": ""})
    assert response.status_code == 422, (
        f"BUG 2: Expected 422 for empty name, got {response.status_code}. "
        f"Body: {response.text}"
    )


def test_create_user_with_whitespace_only_name():
    """BUG 2 variant: name with only spaces must be rejected."""
    response = client.post("/users", json={"name": "   "})
    assert response.status_code == 422, (
        f"BUG 2: Expected 422 for whitespace-only name, got {response.status_code}. "
        f"Body: {response.text}"
    )


def test_create_user_valid_name():
    """Sanity: valid creation works."""
    response = client.post("/users", json={"name": "Bob"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bob"
    assert "id" in data


# ── Bug 3: PUT /users/{id} checks existence ────────────────────────────

def test_update_nonexistent_user_returns_404():
    """BUG 3: updating a non-existent user must return 404, not crash."""
    response = client.put("/users/nonexistent-id", json={"name": "Updated"})
    assert response.status_code == 404, (
        f"BUG 3: Expected 404 for updating missing user, got {response.status_code}. "
        f"Body: {response.text}"
    )


def test_update_existing_user_succeeds():
    """Sanity: updating an existing user works."""
    resp = client.post("/users", json={"name": "Charlie"})
    uid = resp.json()["id"]

    response = client.put(f"/users/{uid}", json={"name": "Charlie Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Charlie Updated"


def test_update_user_partial_succeeds():
    """Updating only name field keeps other fields intact."""
    resp = client.post("/users", json={"name": "Diana"})
    uid = resp.json()["id"]

    response = client.put(f"/users/{uid}", json={"name": "Diana Changed"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Diana Changed"
    assert data["id"] == uid


# ── Edge cases ──────────────────────────────────────────────────────────

def test_list_users_empty():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_with_data():
    client.post("/users", json={"name": "Eve"})
    client.post("/users", json={"name": "Frank"})
    response = client.get("/users")
    assert len(response.json()) == 2


def test_delete_nonexistent_user():
    response = client.delete("/users/nonexistent-id")
    assert response.status_code == 404


def test_delete_existing_user():
    resp = client.post("/users", json={"name": "Grace"})
    uid = resp.json()["id"]
    response = client.delete(f"/users/{uid}")
    assert response.status_code == 204
