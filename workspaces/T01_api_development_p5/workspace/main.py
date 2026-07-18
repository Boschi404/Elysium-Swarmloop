"""
User CRUD API — FastAPI REST service with in-memory storage.

Endpoints:
    GET    /users       — List all users
    GET    /users/{id}  — Get a single user by ID
    POST   /users       — Create a new user
    PUT    /users/{id}  — Update an existing user
    DELETE /users/{id}  — Delete a user

Input validation:
    - email: valid email format
    - name: string with length > 2
    - age: positive integer (> 0)
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import uuid

app = FastAPI(title="User CRUD API")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str = Field(..., min_length=3, description="User name, at least 3 characters")
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be a positive integer")


class UserUpdate(BaseModel):
    """Schema for updating a user. All fields optional."""
    name: Optional[str] = Field(None, min_length=3, description="User name, at least 3 characters")
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be a positive integer")


class UserResponse(BaseModel):
    """Schema returned to the client."""
    id: str
    name: str
    email: str
    age: int


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_db: List[dict] = []


def _find_user(user_id: str) -> Optional[dict]:
    """Return user dict by id, or None if not found."""
    for user in _db:
        if user["id"] == user_id:
            return user
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_users() -> List[dict]:
    """Return all users."""
    return _db


@app.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: str) -> dict:
    """Return a single user by id."""
    user = _find_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> dict:
    """Create a new user."""
    new_id = str(uuid.uuid4())
    user = {
        "id": new_id,
        "name": payload.name,
        "email": payload.email,
        "age": payload.age,
    }
    _db.append(user)
    return user


@app.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: str, payload: UserUpdate) -> dict:
    """Update an existing user. Fields not provided keep their current values."""
    user = _find_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.name is not None:
        user["name"] = payload.name
    if payload.email is not None:
        user["email"] = payload.email
    if payload.age is not None:
        user["age"] = payload.age

    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str) -> None:
    """Delete a user by id."""
    user = _find_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _db.remove(user)
    return None
