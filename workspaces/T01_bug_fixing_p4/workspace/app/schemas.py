from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User name must not be empty")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="User name must not be empty when provided")


class UserOut(BaseModel):
    id: int
    name: str
