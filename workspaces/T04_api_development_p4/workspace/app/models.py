"""Pydantic models for the Blog Post API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """Shared post fields."""

    title: str = Field(..., min_length=1, description="Post title")
    content: str = Field(..., min_length=11, description="Post content (min 10 chars)")
    author: str = Field(..., min_length=1, description="Author name")
    tags: list[str] = Field(default_factory=list, description="Post tags")


class PostCreate(PostBase):
    """Schema for creating a post."""

    pass


class PostUpdate(BaseModel):
    """Schema for updating a post. All fields optional."""

    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=11)
    author: Optional[str] = Field(None, min_length=1)
    tags: Optional[list[str]] = None


class CommentBase(BaseModel):
    """Shared comment fields."""

    content: str = Field(..., min_length=2, description="Comment content (min 1 char)")
    author: str = Field(..., min_length=1, description="Comment author")


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    pass


class Comment(CommentBase):
    """Schema for a comment with server fields."""

    id: int
    post_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class Post(PostBase):
    """Schema for a post with server fields."""

    id: int
    created_at: datetime
    comments: list[Comment] = []

    model_config = {"from_attributes": True}


class PostSummary(BaseModel):
    """Schema for post list items (without comments)."""

    id: int
    title: str
    content: str
    author: str
    tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
