"""Vulnerable search endpoint → parameterized queries (SQL injection fix)."""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Search API", version="1.0.0")

DB_PATH = Path(__file__).parent / "app.db"


def init_db() -> None:
    """Create the items table and seed sample data if empty."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  name TEXT NOT NULL UNIQUE"
            ")"
        )
        cursor = conn.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        if count == 0:
            sample = [
                ("laptop",),
                ("monitor",),
                ("keyboard",),
                ("mouse",),
                ("usb-c hub",),
                ("laptop stand",),
                ("webcam",),
                ("microphone",),
                ("headphones",),
                ("desk lamp",),
            ]
            conn.executemany("INSERT OR IGNORE INTO items (name) VALUES (?)", sample)
            conn.commit()
    finally:
        conn.close()


init_db()


def _get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection."""
    return sqlite3.connect(str(DB_PATH))


# ── Routes ──────────────────────────────────────────────────────────────


@app.get("/")
def read_root():
    """Health-check endpoint."""
    return {"status": "ok"}


@app.get("/search")
def search_items(
    q: str = Query("", description="Search term for item names"),
):
    """
    Search items by name.

    Uses a parameterized query (``?`` placeholder) to prevent SQL injection.
    The original vulnerable code was::

        f"SELECT * FROM items WHERE name LIKE '%{query}%'"

    which allowed arbitrary SQL to be injected via the ``q`` parameter.
    The fix replaces string interpolation with a safe bind parameter.
    """
    search_pattern = f"%{q}%"
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, name FROM items WHERE name LIKE ? ORDER BY id",
            (search_pattern,),
        )
        rows = cursor.fetchall()
        return {"results": [{"id": row[0], "name": row[1]} for row in rows]}
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        conn.close()


@app.post("/items")
def create_item(name: str = Query(..., min_length=1, description="Item name")):
    """Add a new item to the database."""
    conn = _get_connection()
    try:
        conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
        conn.commit()
        return {"status": "created", "name": name}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail=f"Item '{name}' already exists")
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        conn.close()
