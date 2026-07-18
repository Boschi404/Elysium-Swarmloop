from pydantic import BaseModel, Field
from typing import Optional
import uuid


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User name, must not be empty")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Updated user name")


class User(BaseModel):
    id: str
    name: str


def generate_id() -> str:
    return str(uuid.uuid4())
