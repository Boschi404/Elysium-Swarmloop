"""User Service API - T01 Bug Fixing.

Fixes applied:
1. GET /users/{id} — returns 404 via HTTPException when user not found (was None crash)
2. POST /users — validates name is non-empty (was accepting empty strings)
3. PUT /users/{id} — checks user exists before updating (was silent no-op)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI(title="User Service", version="1.0.0")

# In-memory user store
users_db: dict[int, dict] = {}
next_id: int = 1


class UserCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class UserUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name must not be empty")
        return v.strip() if v else v


class UserOut(BaseModel):
    id: int
    name: str


@app.get("/users", response_model=list[UserOut])
def list_users():
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    """FIX #1: Raise 404 when user not found instead of returning None."""
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate):
    """FIX #2: Pydantic validator enforces non-empty name."""
    global next_id
    user = {"id": next_id, "name": body.name}
    users_db[next_id] = user
    next_id += 1
    return user


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate):
    """FIX #3: Check user exists before updating."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    existing = users_db[user_id]
    if body.name is not None:
        existing["name"] = body.name
    return existing
