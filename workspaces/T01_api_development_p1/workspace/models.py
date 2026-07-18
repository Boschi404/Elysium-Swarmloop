"""
Pydantic models for the User CRUD API.
Includes validation for name, email, and age fields.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Input model for creating a new user."""
    name: str = Field(
        ...,
        min_length=3,
        description="User name, must be at least 3 characters",
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address",
    )
    age: int = Field(
        ...,
        gt=0,
        le=150,
        description="User age, must be greater than 0",
    )


class UserUpdate(BaseModel):
    """Input model for updating an existing user. All fields optional."""
    name: Optional[str] = Field(
        None,
        min_length=3,
        description="User name, must be at least 3 characters",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Valid email address",
    )
    age: Optional[int] = Field(
        None,
        gt=0,
        le=150,
        description="User age, must be greater than 0",
    )


class UserResponse(BaseModel):
    """Output model representing a stored user."""
    id: int
    name: str
    email: str
    age: int


class UserInDB(BaseModel):
    """Internal model for in-memory storage."""
    id: int
    name: str
    email: str
    age: int
