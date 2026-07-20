"""
Unit tests for T01 Security Analysis — SQL Injection Detection.
Verifies that the secure version neutralises injection payloads
while the vulnerable version leaks data.

Uses a temporary file for the database so all connections share it.
"""
import sqlite3
import tempfile
import os
import pytest


@pytest.fixture(scope="module")
def db_path():
    """Create a temporary DB file and seed it with sample users."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("INSERT INTO users (username) VALUES ('alice')")
    cursor.execute("INSERT INTO users (username) VALUES ('bob')")
    cursor.execute("INSERT INTO users (username) VALUES ('charlie')")
    conn.commit()
    conn.close()
    yield tmp.name
    os.unlink(tmp.name)


# ═══════════════════════════════════════════════
# VULNERABLE VERSION — demonstrates the flaw
# ═══════════════════════════════════════════════

def get_user_vulnerable(db_path: str, input_val: str) -> list:
    """VULNERABLE: f-string interpolation (DO NOT USE)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{input_val}'")
    results = cursor.fetchall()
    conn.close()
    return results


# ═══════════════════════════════════════════════
# SECURE VERSION — parameterized query
# ═══════════════════════════════════════════════

def get_user_secure(db_path: str, input_val: str) -> list:
    """SECURE: parameterized query with ? placeholder."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (input_val,))
    results = cursor.fetchall()
    conn.close()
    return results


# ═══════════════════════════════════════════════
# TESTS — Vulnerable version
# ═══════════════════════════════════════════════

class TestVulnerableVersion:
    """These tests document the *existence* of the vulnerability."""

    def test_legitimate_input_works(self, db_path):
        """Normal input still works."""
        result = get_user_vulnerable(db_path, "alice")
        assert len(result) == 1
        assert result[0][1] == "alice"

    def test_non_existent_returns_empty(self, db_path):
        """Non-existent username returns empty."""
        result = get_user_vulnerable(db_path, "nobody")
        assert len(result) == 0

    def test_sql_injection_leaks_all_users(self, db_path):
        """SQL injection payload leaks ALL rows (documenting the flaw)."""
        result = get_user_vulnerable(db_path, "' OR '1'='1")
        assert len(result) == 3, (
            f"VULNERABLE: injection payload returned {len(result)} rows "
            f"instead of 0 — attack succeeded!"
        )

    def test_sql_injection_union(self, db_path):
        """UNION-based injection — attacker injects arbitrary data."""
        result = get_user_vulnerable(db_path, "' UNION SELECT 1, 'hacked' --")
        # SQL: SELECT * FROM users WHERE username='' UNION SELECT 1, 'hacked'
        # First SELECT: 0 rows (no user with empty username)
        # UNION SELECT: 1 row (the injected fake record)
        assert len(result) == 1
        assert result[0] == (1, "hacked")

    def test_sql_injection_tautology(self, db_path):
        """Tautology-based injection leaks all users."""
        result = get_user_vulnerable(db_path, "alice' OR '1'='1")
        assert len(result) == 3  # leaks all 3 users


# ═══════════════════════════════════════════════
# TESTS — Secure version (parameterized)
# ═══════════════════════════════════════════════

class TestSecureVersion:
    """These tests assert the parameterized fix works correctly."""

    def test_legitimate_input_works(self, db_path):
        """Normal input works with parameterized query."""
        result = get_user_secure(db_path, "alice")
        assert len(result) == 1
        assert result[0][1] == "alice"

    def test_non_existent_returns_empty(self, db_path):
        """Non-existent username returns empty."""
        result = get_user_secure(db_path, "nobody")
        assert len(result) == 0

    def test_sql_injection_tautology_neutralised(self, db_path):
        """Tautology injection is neutralised — returns empty."""
        result = get_user_secure(db_path, "' OR '1'='1")
        assert len(result) == 0, (
            f"Injection payload returned {len(result)} rows instead of 0 — "
            f"parameterization not working!"
        )

    def test_sql_injection_union_neutralised(self, db_path):
        """UNION injection is neutralised."""
        result = get_user_secure(db_path, "' UNION SELECT 1, 'hacked' --")
        assert len(result) == 0

    def test_sql_injection_comment_neutralised(self, db_path):
        """Comment-based injection is neutralised."""
        result = get_user_secure(db_path, "alice' --")
        assert len(result) == 0, (
            f"Comment injection returned {len(result)} rows — "
            f"SQL injection still possible!"
        )

    def test_destructive_drop_tables_neutralised(self, db_path):
        """Destructive DROP TABLE injection does NOT execute."""
        result = get_user_secure(db_path, "'; DROP TABLE users; --")
        assert len(result) == 0
        # Verify table still exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 3, "TABLE was DROPPED — injection succeeded!"

    def test_special_characters_safe(self, db_path):
        """Special characters in legitimate input handled safely."""
        result = get_user_secure(db_path, "o'brien")
        assert len(result) == 0  # no such user, but no crash
