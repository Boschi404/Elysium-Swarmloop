"""FastAPI Blog Post API — routes for posts and nested comments."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from app.database import init_db, list_posts, get_post, create_post, update_post, delete_post
from app.database import create_comment, delete_comment
from app.models import PostCreate, PostUpdate, CommentCreate, Post, PostSummary, Comment


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Ensure database tables exist on startup."""
    init_db()
    yield


app = FastAPI(title="Blog Post API", version="1.0.0", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------


@app.get("/posts", response_model=list[PostSummary])
def api_list_posts(
    author: str | None = Query(None, description="Filter by author"),
    tag: str | None = Query(None, alias="tag", description="Filter by tag"),
) -> list[dict]:
    """Return a list of posts, optionally filtered."""
    return list_posts(author=author, tag=tag)


@app.get("/posts/{post_id}", response_model=Post)
def api_get_post(post_id: int) -> dict:
    """Return a single post with its comments."""
    post = get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts", response_model=Post, status_code=201)
def api_create_post(data: PostCreate) -> dict:
    """Create a new post."""
    return create_post(data)


@app.put("/posts/{post_id}", response_model=Post)
def api_update_post(post_id: int, data: PostUpdate) -> dict:
    """Update an existing post."""
    updated = update_post(post_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated


@app.delete("/posts/{post_id}", status_code=204)
def api_delete_post(post_id: int) -> None:
    """Delete a post and its comments."""
    if not delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


@app.post("/posts/{post_id}/comments", response_model=Comment, status_code=201)
def api_create_comment(post_id: int, data: CommentCreate) -> dict:
    """Add a comment to a post."""
    comment = create_comment(post_id, data)
    if comment is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return comment


@app.delete("/comments/{comment_id}", status_code=204)
def api_delete_comment(comment_id: int) -> None:
    """Delete a comment."""
    if not delete_comment(comment_id):
        raise HTTPException(status_code=404, detail="Comment not found")
