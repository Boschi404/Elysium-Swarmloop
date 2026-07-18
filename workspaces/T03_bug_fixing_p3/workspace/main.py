"""
Search API — SQL injection fixed with parameterized queries.

The original vulnerable code used string concatenation:
    f"SELECT * FROM items WHERE name LIKE '%{query}%'"

The fix converts to parameterized queries via sqlite3 '?' placeholders,
eliminating SQL injection risk while preserving correct search results.
"""

from fastapi import FastAPI, Query, HTTPException
import sqlite3
import os
from contextlib import asynccontextmanager, closing
from collections.abc import Iterator

@asynccontextmanager
async def lifespan(application: FastAPI) -> Iterator[None]:
    """Initialise database on app startup."""
    init_database()
    yield


app = FastAPI(title="Search API", lifespan=lifespan)

DB_PATH = os.path.join(os.path.dirname(__file__), "items.db")


def get_connection() -> sqlite3.Connection:
    """Create a new database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Seed the database if it's empty."""
    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            """)
            cursor.execute("SELECT COUNT(*) AS cnt FROM items")
            if cursor.fetchone()["cnt"] == 0:
                cursor.executemany(
                    "INSERT INTO items (name, description) VALUES (?, ?)",
                    [
                        ("Laptop", "High-performance laptop computer"),
                        ("Mouse", "Wireless optical mouse"),
                        ("Keyboard", "Mechanical RGB keyboard"),
                        ("Monitor", "27-inch 4K UHD monitor"),
                        ("USB Cable", "USB-C to USB-A charging cable"),
                        ("Headphones", "Noise-cancelling Bluetooth headphones"),
                        ("Webcam", "1080p HD webcam with microphone"),
                    ],
                )
            conn.commit()
    except Exception as exc:
        raise RuntimeError(f"Failed to initialise database: {exc}")


@app.get("/search")
def search_items(
    q: str = Query(..., min_length=1, description="Search query term"),
) -> dict:
    """
    Search items by name or description.

    Uses parameterised queries ('?' placeholders) instead of string
    interpolation to prevent SQL injection attacks.
    """
    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()
            # PARAMETERIZED QUERY — safe from SQL injection.
            # The '?' placeholders are safely bound by the sqlite3 driver,
            # never concatenated into the SQL string.
            cursor.execute(
                "SELECT id, name, description FROM items "
                "WHERE name LIKE ? OR description LIKE ?",
                (f"%{q}%", f"%{q}%"),
            )
            results = [dict(row) for row in cursor.fetchall()]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {exc}",
        )

    return {"results": results, "count": len(results)}


@app.get("/health")
def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "ok"}
