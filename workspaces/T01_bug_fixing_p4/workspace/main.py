"""
User service module — FastAPI with in-memory CRUD.
Three bugs were present, all fixed:
  BUG-1: GET /users/{id} returned None instead of raising 404
  BUG-2: POST /users accepted empty names
  BUG-3: PUT /users/{id} didn't check if user exists before updating
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional


# ── In-memory user store ────────────────────────────────────────────────

class UserNotFoundError(Exception):
    """Raised when a user is not found by id."""
    pass


class _UserDB:
    def __init__(self):
        self._users: dict[int, dict] = {}
        self._next_id = 1

    def create(self, name: str) -> dict:
        user_dict = {"id": self._next_id, "name": name.strip()}
        self._users[self._next_id] = user_dict
        self._next_id += 1
        return dict(user_dict)

    def get(self, user_id: int) -> dict:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return dict(user)

    def get_all(self) -> List[dict]:
        return [dict(u) for u in self._users.values()]

    def update(self, user_id: int, name: Optional[str]) -> dict:
        if user_id not in self._users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if name is not None:
            self._users[user_id]["name"] = name.strip()
        return dict(self._users[user_id])

    def delete(self, user_id: int) -> None:
        if user_id not in self._users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        del self._users[user_id]


db = _UserDB()


# ── Pydantic schemas ────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User name must not be empty")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="User name must not be empty when provided")


class UserOut(BaseModel):
    id: int
    name: str


# ── FastAPI app ─────────────────────────────────────────────────────────

app = FastAPI(title="User Service")


def _handle_not_found(fn):
    try:
        return fn()
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/users", response_model=list[UserOut])
def list_users():
    return db.get_all()


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    """BUG-1: Returns 404 via HTTPException instead of crashing with None."""
    return _handle_not_found(lambda: db.get(user_id))


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate):
    """BUG-2: Empty names rejected by Pydantic min_length=1 on UserCreate.name."""
    return db.create(data.name)


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate):
    """BUG-3: Returns 404 if user does not exist before updating."""
    return _handle_not_found(lambda: db.update(user_id, data.name))


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    _handle_not_found(lambda: db.delete(user_id))
