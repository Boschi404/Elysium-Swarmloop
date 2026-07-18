"""
T01_api_development: User CRUD API
FastAPI REST API for user management with in-memory storage.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List
from uuid import uuid4, UUID

app = FastAPI(title="User CRUD API", version="1.0.0")

# ── In-memory storage ──────────────────────────────────────────────────────

_users_db: dict[str, "User"] = {}

# ── Pydantic models ────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Input model for creating a user."""

    name: str = Field(..., min_length=3, description="User name (min 3 chars)")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be positive")

    @field_validator("name")
    @classmethod
    def name_must_be_longer_than_two(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) <= 2:
            raise ValueError("name must be longer than 2 characters")
        return stripped


class UserUpdate(BaseModel):
    """Input model for updating a user (all fields optional)."""

    name: str | None = Field(None, min_length=3, description="User name (min 3 chars)")
    email: EmailStr | None = Field(None, description="Valid email address")
    age: int | None = Field(None, gt=0, description="Age must be positive")

    @field_validator("name")
    @classmethod
    def name_must_be_longer_than_two(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if len(stripped) <= 2:
                raise ValueError("name must be longer than 2 characters")
            return stripped
        return v


class User(BaseModel):
    """Output model representing a stored user."""

    id: str
    name: str
    email: str
    age: int


# ── Helper ─────────────────────────────────────────────────────────────────


def _get_user_or_404(user_id: str) -> User:
    """Retrieve a user by id or raise 404."""
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return user


# ── CRUD endpoints ─────────────────────────────────────────────────────────


@app.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
def list_users() -> List[User]:
    """Return all stored users."""
    return list(_users_db.values())


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def get_user(user_id: str) -> User:
    """Return a single user by id."""
    return _get_user_or_404(user_id)


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate) -> User:
    """Create a new user."""
    user_id = str(uuid4())
    user = User(id=user_id, name=body.name, email=body.email, age=body.age)
    _users_db[user_id] = user
    return user


@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def update_user(user_id: str, body: UserUpdate) -> User:
    """Update an existing user by id (partial update)."""
    existing = _get_user_or_404(user_id)
    updated_data = existing.model_copy(
        update={
            "name": body.name if body.name is not None else existing.name,
            "email": body.email if body.email is not None else existing.email,
            "age": body.age if body.age is not None else existing.age,
        }
    )
    _users_db[user_id] = updated_data
    return updated_data


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str) -> None:
    """Delete a user by id."""
    _get_user_or_404(user_id)
    del _users_db[user_id]
