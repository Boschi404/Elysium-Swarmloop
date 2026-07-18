"""Tests for User CRUD API."""
import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app, _db, _next_id


@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory DB before each test."""
    _db.clear()
    global _next_id  # noqa: PLW0603
    _next_id = 1
    yield


# ── Helpers ────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Return an async test client."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
def sample_user():
    """Return a valid user payload."""
    return {"name": "Alice Smith", "email": "alice@example.com", "age": 30}


@pytest.fixture
async def created_user(client, sample_user):
    """Create a user via POST and return the response JSON."""
    resp = await client.post("/users", json=sample_user)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()


# ── POST /users — Create ───────────────────────────────────────────────

@pytest.mark.anyio
async def test_create_user(client, sample_user):
    """POST /users should create a user and return 201."""
    resp = await client.post("/users", json=sample_user)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["age"] == 30
    assert data["id"] == 1
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_user_invalid_name_too_short(client):
    """POST /users with name < 3 chars should return 422."""
    resp = await client.post("/users", json={"name": "Ab", "email": "a@b.com", "age": 20})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_user_invalid_email(client):
    """POST /users with invalid email should return 422."""
    resp = await client.post("/users", json={"name": "Bob", "email": "not-an-email", "age": 20})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_user_invalid_age_zero(client):
    """POST /users with age=0 should return 422."""
    resp = await client.post("/users", json={"name": "Bob", "email": "bob@b.com", "age": 0})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_user_invalid_age_negative(client):
    """POST /users with negative age should return 422."""
    resp = await client.post("/users", json={"name": "Bob", "email": "bob@b.com", "age": -5})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_duplicate_email(client, sample_user):
    """POST /users with duplicate email should return 409."""
    await client.post("/users", json=sample_user)
    resp = await client.post("/users", json={"name": "Other", "email": "alice@example.com", "age": 25})
    assert resp.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in resp.json()["detail"]


# ── GET /users — List ──────────────────────────────────────────────────

@pytest.mark.anyio
async def test_list_users_empty(client):
    """GET /users should return an empty list initially."""
    resp = await client.get("/users")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []


@pytest.mark.anyio
async def test_list_users(client, created_user):
    """GET /users should return all created users."""
    # Create a second user
    await client.post("/users", json={"name": "Bob", "email": "bob@example.com", "age": 25})
    resp = await client.get("/users")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "Alice Smith"
    assert data[1]["name"] == "Bob"


# ── GET /users/{id} — Get single ──────────────────────────────────────

@pytest.mark.anyio
async def test_get_user(client, created_user):
    """GET /users/{id} should return the user."""
    resp = await client.get(f"/users/{created_user['id']}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Alice Smith"


@pytest.mark.anyio
async def test_get_user_not_found(client):
    """GET /users/{id} for non-existent id should return 404."""
    resp = await client.get("/users/999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── PUT /users/{id} — Update ──────────────────────────────────────────

@pytest.mark.anyio
async def test_update_user(client, created_user):
    """PUT /users/{id} should update user fields."""
    uid = created_user["id"]
    resp = await client.put(f"/users/{uid}", json={"name": "Alice Updated", "age": 31})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["name"] == "Alice Updated"
    assert data["age"] == 31
    assert data["email"] == "alice@example.com"  # unchanged


@pytest.mark.anyio
async def test_update_user_not_found(client):
    """PUT /users/{id} for non-existent id should return 404."""
    resp = await client.put("/users/999", json={"name": "Ghost"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_user_duplicate_email(client, created_user):
    """PUT /users/{id} with email that exists on another user should return 409."""
    # Create second user
    resp = await client.post("/users", json={"name": "Bob", "email": "bob@example.com", "age": 25})
    bob_id = resp.json()["id"]
    # Try to change Bob's email to Alice's
    resp = await client.put(f"/users/{bob_id}", json={"email": "alice@example.com"})
    assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_update_user_invalid_email(client, created_user):
    """PUT /users/{id} with invalid email should return 422."""
    uid = created_user["id"]
    resp = await client.put(f"/users/{uid}", json={"email": "bad-email"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_update_user_same_email(client, created_user):
    """PUT /users/{id} with the same email should be allowed."""
    uid = created_user["id"]
    resp = await client.put(f"/users/{uid}", json={"email": "alice@example.com"})
    assert resp.status_code == status.HTTP_200_OK


# ── DELETE /users/{id} — Delete ────────────────────────────────────────

@pytest.mark.anyio
async def test_delete_user(client, created_user):
    """DELETE /users/{id} should delete and return 204."""
    uid = created_user["id"]
    resp = await client.delete(f"/users/{uid}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    # Verify it's gone
    resp = await client.get(f"/users/{uid}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_user_not_found(client):
    """DELETE /users/{id} for non-existent id should return 404."""
    resp = await client.delete("/users/999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── Edge cases ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_users_count_after_operations(client, sample_user):
    """Verify user count after create and delete."""
    assert (await client.get("/users")).json() == []
    r1 = await client.post("/users", json=sample_user)
    assert r1.status_code == 201
    assert len((await client.get("/users")).json()) == 1
    await client.delete(f"/users/{r1.json()['id']}")
    assert (await client.get("/users")).json() == []
