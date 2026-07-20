"""User CRUD API — FastAPI with in-memory storage and input validation."""

import re
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="User CRUD API", version="1.0.0")

# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------
users_db: dict[int, dict] = {}
next_id: int = 1

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Request model for creating a new user."""
    name: str = Field(..., min_length=3, description="Full name (min 3 chars)")
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be positive integer")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate email format with a simple regex."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value.strip()):
            raise ValueError("Invalid email format")
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Strip whitespace and enforce minimum length."""
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Name must be at least 3 characters")
        return stripped


class UserUpdate(BaseModel):
    """Request model for updating an existing user (all fields optional)."""
    name: Optional[str] = Field(None, min_length=3, description="Full name (min 3 chars)")
    email: Optional[str] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be positive integer")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value.strip()):
            raise ValueError("Invalid email format")
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Name must be at least 3 characters")
        return stripped


class User(BaseModel):
    """Response model representing a user."""
    id: int
    name: str
    email: str
    age: int


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _to_user(user_id: int, user_data: dict) -> dict:
    """Convert internal storage dict to serialisable user representation."""
    return {"id": user_id, "name": user_data["name"], "email": user_data["email"], "age": user_data["age"]}


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------

@app.get("/users", response_model=list[User], status_code=status.HTTP_200_OK)
def list_users() -> list[dict]:
    """Return all users."""
    return [_to_user(uid, data) for uid, data in users_db.items()]


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def get_user(user_id: int) -> dict:
    """Return a single user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _to_user(user_id, users_db[user_id])


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> dict:
    """Create a new user."""
    global next_id
    user_id = next_id
    next_id += 1
    users_db[user_id] = payload.model_dump()
    return _to_user(user_id, users_db[user_id])


@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate) -> dict:
    """Update an existing user (partial update supported)."""
    if user_id not in users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    users_db[user_id].update(updates)
    return _to_user(user_id, users_db[user_id])


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    """Delete a user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    del users_db[user_id]
