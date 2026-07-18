"""
User CRUD API built with FastAPI.
Stores data in memory. Supports standard CRUD operations:
  GET    /users       — list all users
  GET    /users/{id}  — get a single user
  POST   /users       — create a new user
  PUT    /users/{id}  — update an existing user
  DELETE /users/{id}  — delete a user
"""

import uuid
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models import UserCreate, UserInDB, UserResponse, UserUpdate

app = FastAPI(
    title="User CRUD API",
    description="Simple in-memory user management REST API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store ──────────────────────────────────────────────────────────

_db: dict[int, UserInDB] = {}
_next_id: int = 1


def _next_user_id() -> int:
    global _next_id
    uid = _next_id
    _next_id += 1
    return uid


# ── Helper ───────────────────────────────────────────────────────────────────

def _get_user_or_404(user_id: int) -> UserInDB:
    user = _db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
)
def list_users():
    """Return all stored users."""
    return [UserResponse(**u.model_dump()) for u in _db.values()]


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single user",
)
def get_user(user_id: int):
    """Return a user by their unique ID. 404 if not found."""
    user = _get_user_or_404(user_id)
    return UserResponse(**user.model_dump())


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(payload: UserCreate):
    """Create a new user and return it with the assigned ID."""
    uid = _next_user_id()
    user = UserInDB(id=uid, **payload.model_dump())
    _db[uid] = user
    return UserResponse(**user.model_dump())


@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing user",
)
def update_user(user_id: int, payload: UserUpdate):
    """Partially update a user. Only supplied fields are modified. 404 if not found."""
    user = _get_user_or_404(user_id)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    updated = user.model_copy(update=update_data)
    _db[user_id] = updated
    return UserResponse(**updated.model_dump())


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user(user_id: int):
    """Remove a user from the store. 404 if not found."""
    _get_user_or_404(user_id)
    del _db[user_id]
    return None  # 204 No Content, no response body
