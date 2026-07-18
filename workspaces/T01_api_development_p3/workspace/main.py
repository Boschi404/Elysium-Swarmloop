"""User CRUD API — FastAPI in-memory REST service."""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

app = FastAPI(title="User CRUD API")


# ── Models ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Request model for creating a user."""
    name: str = Field(..., min_length=3, description="User name, min 3 chars")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be positive")

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return stripped


class UserUpdate(BaseModel):
    """Request model for updating a user. All fields optional."""
    name: Optional[str] = Field(None, min_length=3, description="User name, min 3 chars")
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be positive")

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if len(stripped) < 3:
                raise ValueError("Name must be at least 3 characters long")
            return stripped
        return v


class UserResponse(BaseModel):
    """Response model for a user record."""
    id: int
    name: str
    email: str
    age: int


# ── In-Memory Store ─────────────────────────────────────────────────────────

_users_db: dict[int, dict] = {}
_next_id: int = 1


def _get_next_id() -> int:
    """Return the next sequential user ID."""
    global _next_id  # noqa: PLW0603
    uid = _next_id
    _next_id += 1
    return uid


# ── API Routes ──────────────────────────────────────────────────────────────


@app.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_users() -> list[dict]:
    """Return all users."""
    return list(_users_db.values())


@app.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int) -> dict:
    """Return a single user by ID."""
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: UserCreate) -> dict:
    """Create a new user."""
    user = payload.model_dump()
    user_id = _get_next_id()
    user["id"] = user_id
    _users_db[user_id] = user
    return user


@app.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate) -> dict:
    """Update an existing user (partial update supported)."""
    existing = _users_db.get(user_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    updated = payload.model_dump(exclude_unset=True)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    existing.update(updated)
    _users_db[user_id] = existing
    return existing


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    """Delete a user by ID."""
    if user_id not in _users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    del _users_db[user_id]
