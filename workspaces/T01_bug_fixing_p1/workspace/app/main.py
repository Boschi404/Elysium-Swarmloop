"""FastAPI app exposing buggy user endpoints."""

from fastapi import FastAPI, HTTPException, status
from app.models import UserCreate, UserUpdate
from app.service import UserService

app = FastAPI(title="User Service (Buggy)", version="0.1.0")
service = UserService()


@app.get("/users", response_model=list)
def list_users():
    return service.list_users()


@app.get("/users/{user_id}", response_model=UserCreate)
def get_user(user_id: str):
    """BUG 1 surfaces here: service returns None, FastAPI crashes with 500."""
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.post("/users", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    """BUG 2 is in service.create_user — it accepts empty names."""
    return service.create_user(payload)


@app.put("/users/{user_id}", response_model=UserCreate)
def update_user(user_id: str, payload: UserUpdate):
    """BUG 3 is in service.update_user — it doesn't check existence."""
    try:
        return service.update_user(user_id, payload)
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
