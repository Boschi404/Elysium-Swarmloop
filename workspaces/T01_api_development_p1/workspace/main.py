"""FastAPI User CRUD API with in-memory storage."""
from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from typing import List

from models import UserCreate, UserUpdate, UserResponse

app = FastAPI(
    title="User CRUD API",
    description="A REST API for user management with CRUD operations",
    version="1.0.0",
)

# In-memory storage
users_db: dict[int, dict] = {}
next_id: int = 1


@app.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def list_users():
    """Retrieve all users."""
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: int):
    """Retrieve a single user by ID."""
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    global next_id
    now = datetime.utcnow()
    user = {
        "id": next_id,
        "name": user_data.name,
        "email": user_data.email,
        "age": user_data.age,
        "created_at": now,
        "updated_at": now,
    }
    users_db[next_id] = user
    next_id += 1
    return user


@app.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_data: UserUpdate):
    """Update an existing user."""
    current = users_db.get(user_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Apply partial updates
    update_payload = {}
    if user_data.name is not None:
        update_payload["name"] = user_data.name
    if user_data.email is not None:
        update_payload["email"] = user_data.email
    if user_data.age is not None:
        update_payload["age"] = user_data.age

    # Ensure at least one field is being updated
    if not update_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    update_payload["updated_at"] = datetime.utcnow()
    current.update(update_payload)
    return current


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    del users_db[user_id]
    return None
