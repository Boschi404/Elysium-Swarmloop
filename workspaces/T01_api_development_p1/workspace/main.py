"""
FastAPI User Management CRUD API.

Endpoints:
    GET    /users       — List all users
    GET    /users/{id}  — Get a single user by ID
    POST   /users       — Create a new user
    PUT    /users/{id}  — Update an existing user
    DELETE /users/{id}  — Delete a user

All data is stored in memory (no database required).
Input validation: email format, name length > 2, age > 0.
"""

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="User Management API",
    description="Simple in-memory CRUD for users",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Request body for POST /users and PUT /users/{id}."""

    name: str = Field(..., min_length=3, description="User name (min 3 chars)")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., ge=1, description="User age (> 0)")

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) <= 2:
            raise ValueError("name must be longer than 2 characters")
        return stripped

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("age must be greater than 0")
        return v


class UserOut(BaseModel):
    """Response body for a single user (includes auto-generated id)."""

    id: str
    name: str
    email: str
    age: int


class UserUpdate(BaseModel):
    """Optional fields for PUT — reuses the same validation as create."""

    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=1)

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if len(stripped) <= 2:
                raise ValueError("name must be longer than 2 characters")
            return stripped
        return v


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_db: dict[str, dict] = {}


def _user_to_out(record: dict) -> UserOut:
    return UserOut(
        id=record["id"],
        name=record["name"],
        email=record["email"],
        age=record["age"],
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/users", response_model=list[UserOut], status_code=status.HTTP_200_OK)
def list_users():
    """Return every stored user."""
    return [_user_to_out(r) for r in _db.values()]


@app.get(
    "/users/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: str):
    """Return a single user by its UUID."""
    record = _db.get(user_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return _user_to_out(record)


@app.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(body: UserCreate):
    """Create a new user and return it."""
    user_id = str(uuid.uuid4())
    record = {
        "id": user_id,
        "name": body.name,
        "email": body.email,
        "age": body.age,
    }
    _db[user_id] = record
    return _user_to_out(record)


@app.put(
    "/users/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
def update_user(user_id: str, body: UserUpdate):
    """Update an existing user (partial or full). Returns the updated user."""
    record = _db.get(user_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    if body.name is not None:
        record["name"] = body.name
    if body.email is not None:
        record["email"] = body.email
    if body.age is not None:
        record["age"] = body.age

    _db[user_id] = record
    return _user_to_out(record)


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: str):
    """Delete a user. Returns 204 regardless of whether it existed."""
    _db.pop(user_id, None)
    return None
