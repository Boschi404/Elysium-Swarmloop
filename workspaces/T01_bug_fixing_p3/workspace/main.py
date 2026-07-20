"""User Service — FastAPI CRUD with proper error handling.

Fixes applied:
  Bug 1: GET /users/{id} returns 404 instead of crashing on missing user
  Bug 2: POST /users validates name is non-empty (422 on empty/whitespace)
  Bug 3: PUT /users/{id} checks user exists first (404 if not found)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI(title="User Service")

# In-memory store
users_db: dict[int, dict] = {}
next_id = 1


class UserCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name must not be empty")
        return stripped


class UserUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty_if_provided(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Name must not be empty")
            return stripped
        return v


@app.get("/users")
def list_users():
    return list(users_db.values())


@app.get("/users/{user_id}")
def get_user(user_id: int):
    # Bug 1 fix: return 404 instead of crashing on missing user
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    global next_id
    # Bug 2 fix: validation is handled by Pydantic's field_validator above
    user = {"id": next_id, "name": body.name}
    users_db[next_id] = user
    next_id += 1
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, body: UserUpdate):
    # Bug 3 fix: check user exists before updating
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    user = users_db[user_id]
    if body.name is not None:
        user["name"] = body.name
    return user
