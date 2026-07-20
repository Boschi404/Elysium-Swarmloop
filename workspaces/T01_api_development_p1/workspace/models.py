"""Pydantic models for User CRUD API."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    """Request model for creating a user."""
    name: str = Field(..., min_length=3, description="User name, must be > 2 characters")
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be positive")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format with regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class UserUpdate(BaseModel):
    """Request model for updating a user. All fields optional."""
    name: Optional[str] = Field(None, min_length=3, description="User name, must be > 2 characters")
    email: Optional[str] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be positive")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class UserResponse(BaseModel):
    """Response model for a user."""
    id: int
    name: str
    email: str
    age: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
