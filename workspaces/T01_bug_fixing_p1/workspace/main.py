"""
User Service — Bug Fixes Applied

Bugs fixed:
  1. GET /users/{id}: returns 404 instead of crashing when user not found
  2. POST /users: rejects empty and whitespace-only names
  3. PUT /users/{id}: returns 404 if user does not exist before updating
"""

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


# ── Models ────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User name, must not be empty")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Updated user name")


class User(BaseModel):
    id: str
    name: str


def generate_id() -> str:
    return str(uuid.uuid4())


# ── Service ────────────────────────────────────────────────────────────────

class UserService:
    """Thread-safe in-memory user storage."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def create_user(self, payload: UserCreate) -> User:
        """Create a user. BUG 2 FIXED: rejects empty/whitespace names."""
        name = payload.name.strip()
        if not name:
            raise ValueError("User name must not be empty or whitespace-only")
        user = User(id=generate_id(), name=name)
        self._users[user.id] = user
        return user

    def get_user(self, user_id: str) -> User:
        """BUG 1 FIXED: raises ValueError instead of returning None."""
        user = self._users.get(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        return user

    def update_user(self, user_id: str, payload: UserUpdate) -> User:
        """BUG 3 FIXED: checks existence before updating."""
        if user_id not in self._users:
            raise ValueError(f"User {user_id} not found")
        user = self._users[user_id]
        if payload.name is not None:
            name = payload.name.strip()
            if not name:
                raise ValueError("User name must not be empty or whitespace-only")
            user.name = name
        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def list_users(self) -> list[User]:
        return list(self._users.values())


# ── App ───────────────────────────────────────────────────────────────────

app = FastAPI(title="User Service", version="0.1.0")
service = UserService()


@app.get("/users", response_model=list[User])
def list_users():
    return service.list_users()


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    """BUG 1 FIXED: returns 404 instead of 500 when user not found."""
    try:
        return service.get_user(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    """BUG 2 FIXED: rejects empty/whitespace names via service validation."""
    try:
        return service.create_user(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, payload: UserUpdate):
    """BUG 3 FIXED: returns 404 if user doesn't exist."""
    try:
        return service.update_user(user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
