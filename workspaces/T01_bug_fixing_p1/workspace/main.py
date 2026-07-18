"""FastAPI application — user CRUD endpoints.

BUGS FIXED:
1. GET /users/{id} — was crashing with 500 on missing user (None returned instead of 404)
2. POST /users — was accepting empty names (missing validation)
3. PUT /users/{id} — was not checking if user exists before updating
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

# ─── Models ────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()


class UserUpdate(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip() if v else v


class User(BaseModel):
    id: int
    name: str


# ─── In-memory store ───────────────────────────────────────────────────────

_users: list[User] = []
_next_id: int = 1


def reset_store() -> None:
    global _users, _next_id
    _users.clear()
    _next_id = 1


# ─── Service layer ─────────────────────────────────────────────────────────

def create_user(data: UserCreate) -> User:
    global _next_id
    user = User(id=_next_id, name=data.name)
    _users.append(user)
    _next_id += 1
    return user


def get_user(user_id: int) -> Optional[User]:
    for u in _users:
        if u.id == user_id:
            return u
    return None


def get_all_users() -> list[User]:
    return list(_users)


def update_user(user_id: int, data: UserUpdate) -> Optional[User]:
    for i, u in enumerate(_users):
        if u.id == user_id:
            if data.name is not None:
                _users[i] = User(id=user_id, name=data.name)
            return _users[i]
    return None


def delete_user(user_id: int) -> bool:
    for i, u in enumerate(_users):
        if u.id == user_id:
            _users.pop(i)
            return True
    return False


# ─── FastAPI app ───────────────────────────────────────────────────────────

app = FastAPI(title="User Service")


@app.get("/users", response_model=list[User])
def list_users():
    return get_all_users()


@app.post("/users", response_model=User, status_code=201)
def add_user(body: UserCreate):
    """Bug #2 fixed: Pydantic validates name — empty names rejected as 422."""
    return create_user(body)


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    """Bug #1 fixed: returns 404 when user not found instead of crashing."""
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=User)
def replace_user(user_id: int, body: UserUpdate):
    """Bug #3 fixed: checks user exists before updating, returns 404 if missing."""
    existing = update_user(user_id, body)
    if existing is None:
        raise HTTPException(status_code=404, detail="User not found")
    return existing


@app.delete("/users/{user_id}", status_code=204)
def remove_user(user_id: int):
    deleted = delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
