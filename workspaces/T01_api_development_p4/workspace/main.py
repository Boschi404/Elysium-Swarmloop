"""User CRUD API — FastAPI application with in-memory storage.

Endpoints:
- GET    /users        — List all users
- GET    /users/{id}   — Get a single user by ID
- POST   /users        — Create a new user
- PUT    /users/{id}   — Update an existing user
- DELETE /users/{id}   — Delete a user
"""
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, status

from models import UserCreate, UserInDB, UserResponse, UserUpdate

app = FastAPI(
    title="User CRUD API",
    description="REST API for user management with in-memory storage",
    version="1.0.0",
)

# ── In-memory storage ──────────────────────────────────────────────────
_db: List[UserInDB] = []
_next_id: int = 1


# ── Helper ─────────────────────────────────────────────────────────────
def _find_user(user_id: int) -> UserInDB:
    """Return user by id or raise 404."""
    for user in _db:
        if user.id == user_id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {user_id} not found",
    )


def _to_response(user: UserInDB) -> UserResponse:
    """Convert internal model to response schema."""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


def _is_duplicate_email(email: str, exclude_id: int | None = None) -> bool:
    """Check if email already exists (optional exclude for updates)."""
    for user in _db:
        if user.email == email and user.id != exclude_id:
            return True
    return False


# ── Endpoints ──────────────────────────────────────────────────────────


@app.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_users():
    """Return all users."""
    return [_to_response(u) for u in _db]


@app.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int):
    """Return a single user by ID."""
    return _to_response(_find_user(user_id))


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: UserCreate):
    """Create a new user."""
    global _next_id

    # Check duplicate email
    if _is_duplicate_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' already exists",
        )

    now = datetime.now(timezone.utc)
    user = UserInDB(
        id=_next_id,
        name=payload.name,
        email=payload.email,
        age=payload.age,
        created_at=now,
        updated_at=now,
    )
    _db.append(user)
    _next_id += 1
    return _to_response(user)


@app.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate):
    """Update an existing user (partial update)."""
    user = _find_user(user_id)

    # Check duplicate email on update
    if payload.email is not None and _is_duplicate_email(payload.email, exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' already exists",
        )

    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    if payload.age is not None:
        user.age = payload.age
    user.updated_at = datetime.now(timezone.utc)

    return _to_response(user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """Delete a user by ID."""
    user = _find_user(user_id)
    _db.remove(user)
    return None
