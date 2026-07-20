"""
T01 Security Analysis — SQL Injection Detection
Fixed implementation using parameterized queries.
"""

import sqlite3
from typing import Optional


def vulnerable_lookup(username: str) -> list:
    """
    VULNERABLE: f-string interpolation of user input into SQL query.
    DO NOT USE — included for documentation only.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT)")
    cursor.execute("INSERT INTO users VALUES ('alice')")
    cursor.execute("INSERT INTO users VALUES ('bob')")
    # VULNERABLE LINE:
    cursor.execute(f"SELECT * FROM users WHERE username='{username}'")  # noqa
    return cursor.fetchall()


def safe_lookup(username: str) -> list:
    """
    SAFE: Uses parameterized query with ? placeholder.
    User input is bound as data, never parsed as SQL code.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT)")
    cursor.execute("INSERT INTO users VALUES ('alice')")
    cursor.execute("INSERT INTO users VALUES ('bob')")
    # SAFE — parameterized query:
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    return cursor.fetchall()


def safe_lookup_named(username: str) -> list:
    """
    SAFE: Uses named placeholder style.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT)")
    cursor.execute("INSERT INTO users VALUES ('alice')")
    cursor.execute("INSERT INTO users VALUES ('bob')")
    cursor.execute(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    )
    return cursor.fetchall()


def injection_demo(attack_input: str) -> Optional[str]:
    """
    Demonstrates SQL injection by running the vulnerable query
    with a crafted input and returning the unexpected result.
    Returns a description of what was extracted.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Set up data including a 'secrets' table for exfiltration demo
    cursor.execute("CREATE TABLE users (username TEXT)")
    cursor.execute("CREATE TABLE secrets (data TEXT)")
    cursor.execute("INSERT INTO users VALUES ('alice')")
    cursor.execute("INSERT INTO users VALUES ('bob')")
    cursor.execute("INSERT INTO secrets VALUES ('credit_card: 4111-1111-1111-1111')")
    cursor.execute("INSERT INTO secrets VALUES ('password: s3cret!')")

    try:
        # VULNERABLE: f-string injection
        cursor.execute(f"SELECT * FROM users WHERE username='{attack_input}'")
        rows = cursor.fetchall()
        if rows:
            return f"EXTRACTED: {rows}"
        return "No rows returned"
    except Exception as e:
        return f"Query failed (may have crashed the database): {e}"


# Attack demonstration
if __name__ == "__main__":
    print("=== Secure lookup (parameterized) ===")
    result = safe_lookup("alice")
    print(f"  Result: {result}")

    print("\n=== SQL Injection Demo ===")
    # This input would cause the VULNERABLE query to return ALL users
    attack = "' OR '1'='1"
    print(f"  Attack input: {attack!r}")
    print(f"  VULNERABLE query would produce:")
    print(f"    SELECT * FROM users WHERE username='{attack}'")
    print(f"  Injection result: {injection_demo(attack)}")

    attack2 = "' UNION SELECT data FROM secrets --"
    print(f"\n  Attack input: {attack2!r}")
    print(f"  Injection result: {injection_demo(attack2)}")

    print("\n✅ Parameterized queries prevent all of the above.")
