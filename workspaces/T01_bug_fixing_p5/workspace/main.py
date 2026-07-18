"""
User Service — FastAPI module with all three bugs fixed.

Bug fixes:
  1. GET /users/{id}: was returning None on missing user → now raises 404
  2. POST /users: was accepting empty names → now validates non-empty
  3. PUT /users/{id}: was not checking user existence → now returns 404 if missing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI(title="User Service")

# In-memory user store
users_db: dict[int, dict] = {}
next_id: int = 1


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


class UserOut(BaseModel):
    id: int
    name: str


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate):
    global next_id
    user = {"id": next_id, "name": payload.name}
    users_db[next_id] = user
    next_id += 1
    return user


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    user = users_db[user_id]
    if payload.name is not None:
        stripped = payload.name.strip()
        if not stripped:
            raise HTTPException(status_code=422, detail="name must not be empty")
        user["name"] = stripped
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None
