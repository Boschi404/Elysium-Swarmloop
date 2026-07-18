"""User Service — FastAPI CRUD with proper error handling.

Bug fixes applied:
  1. GET /users/{id} → returns 404 if user not found (was: None crash)
  2. POST /users → rejects empty names (was: accepted silently)
  3. PUT /users/{id} → checks user exists before updating (was: ignored missing user)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
import uuid

app = FastAPI(title="User Service")

# In-memory store
users_db: dict[str, dict] = {}


# ── Models ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("name must not be empty")
        return stripped


class UserUpdate(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("name must not be empty")
            return stripped
        return v


class UserResponse(BaseModel):
    id: str
    name: str


# ── Routes ──────────────────────────────────────────────────────────

@app.get("/users", response_model=list[UserResponse])
def list_users():
    """Return all users."""
    return [
        UserResponse(id=uid, name=u["name"])
        for uid, u in users_db.items()
    ]


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """Return a user by ID, or 404 if not found."""
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user_id, name=user["name"])


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate):
    """Create a new user. Rejects empty names."""
    user_id = str(uuid.uuid4())
    users_db[user_id] = {"name": payload.name}
    return UserResponse(id=user_id, name=payload.name)


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, payload: UserUpdate):
    """Update a user's name. Returns 404 if user does not exist."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        users_db[user_id]["name"] = payload.name
    return UserResponse(id=user_id, name=users_db[user_id]["name"])


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str):
    """Delete a user. Returns 404 if not found."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
