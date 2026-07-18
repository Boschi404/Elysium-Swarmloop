"""
Flask application with a search endpoint.

VULNERABLE version (original):
    cur.execute(f"SELECT * FROM items WHERE name LIKE '%{query}%'")

FIXED version (current):
    cur.execute("SELECT * FROM items WHERE name LIKE ?", (f'%{query}%',))

Uses parameterized queries to prevent SQL injection.
"""

import sqlite3
import os

from flask import Flask, jsonify, request, g

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), "items.db")


def get_db():
    """Get a database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of a request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the items table and seed sample data."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL
        )
        """
    )
    # Seed data if table is empty
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        sample = [
            ("Laptop Pro 15", "High-performance laptop", 1499.99),
            ("Wireless Mouse", "Ergonomic wireless mouse", 29.99),
            ("USB-C Hub", "7-in-1 USB-C adapter", 49.99),
            ("Mechanical Keyboard", "RGB mechanical keyboard", 119.99),
            ("4K Monitor 27", "Ultra HD 27-inch monitor", 599.99),
            ("Noise Cancelling Headphones", "Over-ear Bluetooth headphones", 299.99),
            ("Webcam HD", "1080p webcam with microphone", 89.99),
            ("External SSD 1TB", "Portable USB-C SSD", 139.99),
            ("Docking Station", "Thunderbolt 4 dock", 249.99),
            ("Smartphone Stand", "Adjustable aluminum stand", 24.99),
        ]
        cursor.executemany(
            "INSERT INTO items (name, description, price) VALUES (?, ?, ?)", sample
        )
    conn.commit()
    conn.close()


@app.teardown_appcontext
def teardown(exception=None):
    close_db(exception)


@app.route("/search", methods=["GET"])
def search_items():
    """
    Search items by name (case-insensitive LIKE).

    GET /search?q=term

    Returns JSON array of matching items.
    Uses parameterized query — NO SQL injection possible.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Missing search term 'q'"}), 400

    try:
        db = get_db()
        cur = db.execute(
            "SELECT id, name, description, price FROM items WHERE name LIKE ?",
            (f"%{query}%",),
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    results = [dict(row) for row in rows]
    return jsonify({"results": results, "count": len(results)})


@app.route("/items", methods=["GET"])
def get_all_items():
    """Return every item in the database."""
    db = get_db()
    rows = db.execute("SELECT id, name, description, price FROM items").fetchall()
    return jsonify({"results": [dict(r) for r in rows]})


@app.route("/health", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(debug=False)
