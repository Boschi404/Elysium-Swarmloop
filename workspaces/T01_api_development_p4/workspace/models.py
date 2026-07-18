"""Pydantic models for User CRUD API - Input validation and response schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with shared fields."""
    name: str = Field(..., min_length=3, description="User name, minimum 3 characters")
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, description="Age must be greater than 0")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format manually (without EmailStr dependency)."""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for partial user update (all fields optional)."""
    name: Optional[str] = Field(None, min_length=3, description="User name, minimum 3 characters")
    email: Optional[str] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, description="Age must be greater than 0")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is None:
            return v
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()


class UserResponse(UserBase):
    """Schema for API response with user ID and timestamps."""
    id: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class UserInDB(UserBase):
    """Internal user representation stored in memory."""
    id: int
    created_at: datetime
    updated_at: datetime
