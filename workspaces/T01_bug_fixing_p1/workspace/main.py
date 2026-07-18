"""User CRUD API — Fixed version.

Bug fixes applied:
  1. GET /users/{id} — now returns 404 instead of crashing on missing user
  2. POST /users — rejects empty/invalid names via Pydantic validation
  3. PUT /users/{id} — now checks user exists before updating
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="User CRUD API", version="1.0.0")

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_users_db: List[dict] = []
_next_id: int = 1


def _reset_db() -> None:
    """Reset the in-memory database (useful for tests)."""
    global _users_db, _next_id  # noqa: PLW0603
    _users_db = []
    _next_id = 1


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    """Request body for creating a user."""

    name: str = Field(..., min_length=1, description="Name must not be empty")
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be greater than 0")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject empty/whitespace-only names."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Name must not be empty or whitespace only")
        return stripped

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Ensure email contains '@' and a domain."""
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format — must contain '@' and a domain")
        return value.lower().strip()


class UserUpdate(BaseModel):
    """Request body for updating a user. All fields optional."""

    name: Optional[str] = Field(None, min_length=1, description="Name must not be empty")
    email: Optional[str] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be greater than 0")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Reject empty/whitespace-only names on update too."""
        if value is not None:
            stripped = value.strip()
            if not stripped:
                raise ValueError("Name must not be empty or whitespace only")
            return stripped
        return None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        """Ensure email contains '@' and a domain if provided."""
        if value is not None:
            if "@" not in value or "." not in value.split("@")[-1]:
                raise ValueError("Invalid email format — must contain '@' and a domain")
            return value.lower().strip()
        return None


class UserResponse(BaseModel):
    """Response schema for a user."""

    id: int
    name: str
    email: str
    age: int


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_user(user_id: int) -> dict:
    """Return user dict by id, or raise 404 if not found."""
    for user in _users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {user_id} not found",
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_users() -> List[dict]:
    """Return all users."""
    return list(_users_db)


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: int) -> dict:
    """Return a single user by id. Returns 404 if not found."""
    return _find_user(user_id)


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(body: UserCreate) -> dict:
    """Create a new user. Rejects empty names via Pydantic validation."""
    global _next_id  # noqa: PLW0603
    user = {
        "id": _next_id,
        "name": body.name.strip(),
        "email": body.email,
        "age": body.age,
    }
    _users_db.append(user)
    _next_id += 1
    return user


@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user(user_id: int, body: UserUpdate) -> dict:
    """Update an existing user (partial update). Raises 404 if user not found."""
    user = _find_user(user_id)
    if body.name is not None:
        user["name"] = body.name.strip()
    if body.email is not None:
        user["email"] = body.email
    if body.age is not None:
        user["age"] = body.age
    return user


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: int) -> None:
    """Delete a user by id. Raises 404 if not found."""
    user = _find_user(user_id)
    _users_db.remove(user)
    return None
