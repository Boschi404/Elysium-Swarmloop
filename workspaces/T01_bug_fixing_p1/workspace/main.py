"""
User Service — Fixed version.

Bug fixes applied:
  1. GET /users/{id} — returns 404 via HTTPException instead of crashing on None
  2. POST /users — validates non-empty name (422 on empty/missing)
  3. PUT /users/{id} — checks user exists before update (404 if missing)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI(title="User Service")

# In-memory user store
users_db: dict[int, dict] = {}
next_id = 1


# ── Schemas ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class UserUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class UserOut(BaseModel):
    id: int
    name: str


# ── Endpoints ────────────────────────────────────────────────

@app.get("/users")
def list_users():
    """Return all users."""
    return list(users_db.values())


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """
    Get a single user by ID.
    Bug 1 FIX: raise 404 instead of returning None (crash).
    """
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    """
    Create a new user.
    Bug 2 FIX: Pydantic validator rejects empty names → 422.
    """
    global next_id
    new_id = next_id
    next_id += 1
    user = UserOut(id=new_id, name=body.name)
    users_db[new_id] = user.model_dump()
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, body: UserUpdate):
    """
    Update an existing user.
    Bug 3 FIX: check user exists before updating, raise 404 if missing.
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    updated = UserOut(id=user_id, name=body.name)
    users_db[user_id] = updated.model_dump()
    return updated
