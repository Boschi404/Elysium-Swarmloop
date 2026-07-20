"""
User Service — Fixed version.

Bugs fixed:
  1. GET /users/{id} returns 404 instead of crashing when user not found
  2. POST /users rejects empty names with 422
  3. PUT /users/{id} checks user existence before updating
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# In-memory store & auto-increment id
# ---------------------------------------------------------------------------
users_db: list[dict] = []
next_id: int = 1


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User full name (required, non-empty)")
    email: str = Field(default="", description="Email address")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="User full name")
    email: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_user_index(user_id: int) -> int | None:
    """Return the list index of *user_id*, or ``None`` if not found."""
    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            return i
    return None


def _raise_if_missing(user_id: int) -> dict:
    """Look up a user and raise 404 if absent."""
    idx = _find_user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[idx]


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(title="User Service", version="1.0.0")


@app.get("/users", response_model=list[UserOut])
def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    return users_db[skip : skip + limit]


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    """
    BUG 1 — FIXED: raises 404 when the user does not exist instead of
    returning ``None`` (which caused a 500 crash).
    """
    user = _raise_if_missing(user_id)
    return user


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    """
    BUG 2 — FIXED: ``name`` has ``min_length=1`` in the Pydantic model so
    empty strings are rejected at the validation layer (422) before the
    handler is reached.
    """
    global next_id
    record = {"id": next_id, "name": payload.name, "email": payload.email}
    users_db.append(record)
    next_id += 1
    return record


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate):
    """
    BUG 3 — FIXED: first checks user existence via _find_user_index,
    raising 404 if not found, then applies the partial update.
    """
    idx = _find_user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")

    record = users_db[idx]
    if payload.name is not None:
        record["name"] = payload.name
    if payload.email is not None:
        record["email"] = payload.email
    users_db[idx] = record
    return record


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    idx = _find_user_index(user_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="User not found")
    users_db.pop(idx)
    return None
