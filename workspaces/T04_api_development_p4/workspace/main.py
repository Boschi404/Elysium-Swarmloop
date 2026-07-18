"""
Blog Post API with Comments
============================
FastAPI implementation with in-memory storage.
Endpoints: CRUD posts + nested comments with content validation.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Blog Post API")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class PostCreate(BaseModel):
    """Schema for creating a new post."""
    title: str = Field(..., min_length=1, description="Post title")
    content: str = Field(..., description="Post content (> 10 characters)")
    author: str = Field(..., min_length=1, description="Author name")
    tags: list[str] = Field(default_factory=list, description="List of tags")

    @field_validator("content")
    @classmethod
    def content_must_be_longer_than_10(cls, v: str) -> str:
        if len(v.strip()) <= 10:
            raise ValueError("Post content must be longer than 10 characters")
        return v.strip()


class PostUpdate(BaseModel):
    """Schema for updating an existing post (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None)
    author: Optional[str] = Field(None, min_length=1)
    tags: Optional[list[str]] = None

    @field_validator("content")
    @classmethod
    def content_must_be_longer_than_10(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) <= 10:
            raise ValueError("Post content must be longer than 10 characters")
        return v.strip() if v is not None else None


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""
    content: str = Field(..., description="Comment content (> 1 character)")
    author: str = Field(..., min_length=1, description="Comment author")

    @field_validator("content")
    @classmethod
    def content_must_be_longer_than_1(cls, v: str) -> str:
        if len(v.strip()) <= 1:
            raise ValueError("Comment content must be longer than 1 character")
        return v.strip()


class CommentOut(BaseModel):
    """Schema for returning a comment."""
    id: int
    post_id: int
    content: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    """Schema for returning a post (without comments)."""
    id: int
    title: str
    content: str
    author: str
    tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PostWithComments(PostOut):
    """Schema for returning a post with its nested comments."""
    comments: list[CommentOut] = []


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_posts: dict[int, dict] = {}
_comments: dict[int, dict] = {}
_next_post_id: int = 1
_next_comment_id: int = 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helper — raise 404 if a post does not exist
# ---------------------------------------------------------------------------

def _get_post_or_404(post_id: int) -> dict:
    post = _posts.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# ---------------------------------------------------------------------------
# Endpoints — Posts
# ---------------------------------------------------------------------------


@app.get("/posts", response_model=list[PostOut])
def list_posts(
    author: Optional[str] = Query(None, description="Filter by author"),
    tag: Optional[str] = Query(None, description="Filter by tag (exact match)"),
) -> list[dict]:
    """Return all posts, optionally filtered by author and/or tag."""
    results = list(_posts.values())

    if author is not None:
        results = [p for p in results if p["author"] == author]

    if tag is not None:
        results = [p for p in results if tag in p["tags"]]

    # Return newest first
    results.sort(key=lambda p: p["created_at"], reverse=True)
    return results


@app.get("/posts/{post_id}", response_model=PostWithComments)
def get_post(post_id: int) -> dict:
    """Return a single post with all its comments."""
    post = _get_post_or_404(post_id)
    post_comments = [
        c for c in _comments.values() if c["post_id"] == post_id
    ]
    post_comments.sort(key=lambda c: c["created_at"])
    return {**post, "comments": post_comments}


@app.post("/posts", response_model=PostOut, status_code=201)
def create_post(body: PostCreate) -> dict:
    """Create a new blog post."""
    global _next_post_id
    post_id = _next_post_id
    _next_post_id += 1

    post = {
        "id": post_id,
        "title": body.title.strip(),
        "content": body.content,
        "author": body.author.strip(),
        "tags": body.tags,
        "created_at": _now(),
    }
    _posts[post_id] = post
    return post


@app.put("/posts/{post_id}", response_model=PostOut)
def update_post(post_id: int, body: PostUpdate) -> dict:
    """Update an existing blog post (partial update)."""
    post = _get_post_or_404(post_id)

    if body.title is not None:
        post["title"] = body.title.strip()
    if body.content is not None:
        post["content"] = body.content
    if body.author is not None:
        post["author"] = body.author.strip()
    if body.tags is not None:
        post["tags"] = body.tags

    return post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int) -> None:
    """Delete a post and its associated comments."""
    _get_post_or_404(post_id)  # raises 404 if missing
    del _posts[post_id]

    # Cascade-delete comments belonging to this post
    to_remove = [cid for cid, c in _comments.items() if c["post_id"] == post_id]
    for cid in to_remove:
        del _comments[cid]


# ---------------------------------------------------------------------------
# Endpoints — Comments
# ---------------------------------------------------------------------------


@app.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(post_id: int, body: CommentCreate) -> dict:
    """Add a comment to an existing post."""
    _get_post_or_404(post_id)  # post must exist

    global _next_comment_id
    comment_id = _next_comment_id
    _next_comment_id += 1

    comment = {
        "id": comment_id,
        "post_id": post_id,
        "content": body.content,
        "author": body.author.strip(),
        "created_at": _now(),
    }
    _comments[comment_id] = comment
    return comment


@app.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int) -> None:
    """Delete a comment by its ID."""
    if comment_id not in _comments:
        raise HTTPException(status_code=404, detail="Comment not found")
    del _comments[comment_id]
