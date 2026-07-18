"""
FastAPI user service.
Bugs fixed:
  1. GET /users/{id} — raises 404 via HTTPException instead of returning None
  2. POST /users — rejects empty names via Pydantic validation
  3. PUT /users/{id} — checks user existence before applying update
"""

from fastapi import FastAPI, HTTPException, status
from app.schemas import UserCreate, UserUpdate, UserOut
from app.service import db, UserNotFoundError

app = FastAPI(title="User Service")


def _handle_not_found(fn):
    """Decorator-like helper to convert UserNotFoundError to 404."""
    try:
        return fn()
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/users", response_model=list[UserOut])
def list_users():
    return db.get_all()


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    return _handle_not_found(lambda: db.get(user_id))


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate):
    """Empty names are rejected by Pydantic (min_length=1 on UserCreate.name)."""
    return db.create(data)


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate):
    """Raises 404 if user does not exist (BUG-3 fix)."""
    return _handle_not_found(lambda: db.update(user_id, data))


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    _handle_not_found(lambda: db.delete(user_id))
