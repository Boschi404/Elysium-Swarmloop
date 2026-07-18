"""SQLite database setup and operations for the Blog Post API."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models import PostCreate, PostUpdate, CommentCreate

DB_PATH = Path(__file__).resolve().parent.parent / "blog.db"


def get_connection() -> sqlite3.Connection:
    """Return a new database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def list_posts(author: Optional[str] = None, tag: Optional[str] = None) -> list[dict]:
    """Return posts, optionally filtered by author and/or tag."""
    conn = get_connection()
    try:
        conditions: list[str] = []
        params: list[str] = []

        if author:
            conditions.append("author = ?")
            params.append(author)
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")

        where = ""
        if conditions:
            where = "WHERE " + " AND ".join(conditions)

        rows = conn.execute(
            f"SELECT * FROM posts {where} ORDER BY created_at DESC",
            params,
        ).fetchall()
        return [_row_to_post(r) for r in rows]
    finally:
        conn.close()


def get_post(post_id: int) -> Optional[dict]:
    """Return a single post with comments, or None."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if row is None:
            return None
        post = _row_to_post(row)
        post["comments"] = _get_comments_for_post(conn, post_id)
        return post
    finally:
        conn.close()


def create_post(data: PostCreate) -> dict:
    """Insert a new post and return it."""
    now = datetime.utcnow().isoformat()
    tags_str = ",".join(data.tags) if data.tags else ""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO posts (title, content, author, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            (data.title, data.content, data.author, tags_str, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_post(row)
    finally:
        conn.close()


def update_post(post_id: int, data: PostUpdate) -> Optional[dict]:
    """Update an existing post. Returns updated post or None if not found."""
    conn = get_connection()
    try:
        existing = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if existing is None:
            return None

        title = data.title if data.title is not None else existing["title"]
        content = data.content if data.content is not None else existing["content"]
        author = data.author if data.author is not None else existing["author"]
        tags = data.tags if data.tags is not None else existing["tags"]
        tags_str = ",".join(tags) if isinstance(tags, list) else tags

        conn.execute(
            "UPDATE posts SET title=?, content=?, author=?, tags=? WHERE id=?",
            (title, content, author, tags_str, post_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        return _row_to_post(row)
    finally:
        conn.close()


def delete_post(post_id: int) -> bool:
    """Delete a post and its comments. Returns True if deleted."""
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def create_comment(post_id: int, data: CommentCreate) -> Optional[dict]:
    """Add a comment to a post. Returns the comment or None if post not found."""
    conn = get_connection()
    try:
        post = conn.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post is None:
            return None

        now = datetime.utcnow().isoformat()
        cur = conn.execute(
            "INSERT INTO comments (post_id, content, author, created_at) VALUES (?, ?, ?, ?)",
            (post_id, data.content, data.author, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM comments WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_comment(row)
    finally:
        conn.close()


def delete_comment(comment_id: int) -> bool:
    """Delete a comment. Returns True if deleted."""
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_comments_for_post(conn: sqlite3.Connection, post_id: int) -> list[dict]:
    """Return all comments for a post."""
    rows = conn.execute(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC",
        (post_id,),
    ).fetchall()
    return [_row_to_comment(r) for r in rows]


def _row_to_post(row: sqlite3.Row) -> dict:
    """Convert a posts row to a dict."""
    tags_raw = row["tags"]
    tags = tags_raw.split(",") if tags_raw else []
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "author": row["author"],
        "tags": tags,
        "created_at": row["created_at"],
    }


def _row_to_comment(row: sqlite3.Row) -> dict:
    """Convert a comments row to a dict."""
    return {
        "id": row["id"],
        "post_id": row["post_id"],
        "content": row["content"],
        "author": row["author"],
        "created_at": row["created_at"],
    }
