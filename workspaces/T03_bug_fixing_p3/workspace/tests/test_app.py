"""
Tests for the search endpoint, verifying:
1. Parameterized queries prevent SQL injection
2. Correct results are returned
3. Edge cases are handled
"""

import json
import os
import sys
import sqlite3
import tempfile

import pytest


# Ensure the workspace is on sys.path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app, init_db, DATABASE


@pytest.fixture
def client():
    """Create a test client with a temporary database."""
    # Override DATABASE with a temp file for testing
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(tmp_fd)

    app.config["TESTING"] = True

    # Monkey-patch the DATABASE path
    import main as app_module

    original_db = app_module.DATABASE
    app_module.DATABASE = tmp_path

    # Init the temp DB
    init_db()

    with app.test_client() as c:
        yield c

    # Cleanup
    app_module.DATABASE = original_db
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


# ── Functional correctness tests ──────────────────────────────


def test_search_returns_matching_items(client):
    """Search for 'laptop' should return items containing 'laptop'."""
    resp = client.get("/search?q=laptop")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1
    names = [r["name"] for r in data["results"]]
    assert any("Laptop" in n for n in names)


def test_search_case_insensitive(client):
    """LIKE is case-insensitive on most SQLite setups."""
    resp = client.get("/search?q=LAPTOP")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1


def test_search_partial_match(client):
    """Partial substring match should work."""
    resp = client.get("/search?q=board")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1
    names = [r["name"] for r in data["results"]]
    assert any("Keyboard" in n for n in names)


def test_search_no_match(client):
    """A term with no match should return an empty array."""
    resp = client.get("/search?q=zzzznotfoundxxxx")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 0
    assert data["results"] == []


def test_search_multiple_matches(client):
    """Search for 'USB' should return both 'USB-C Hub' and 'External SSD' etc."""
    resp = client.get("/search?q=USB")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1


# ── SQL injection prevention tests ────────────────────────────


def test_sql_injection_union_returns_single_item(client):
    """Classic UNION injection: ' OR 1=1 UNION SELECT ...' returns only the
    matching row, NOT a dump of other tables."""
    resp = client.get("/search?q=" + "' OR 1=1 UNION SELECT 1,2,3,4 --")
    assert resp.status_code == 200
    data = resp.get_json()

    # With a vulnerable query this would return 10+ items (all rows),
    # or reveal the 3rd / 4th column.  With parameterised queries
    # the literal string is searched for — unlikely to match anything.
    assert data["count"] == 0, (
        "SQL injection via UNION should not return extra rows. "
        f"Got {data['count']} results."
    )


def test_sql_injection_tautology_returns_zero(client):
    """Tautology injection: ' OR 1=1 -- would return ALL items in a
    vulnerable app.  Parameterised queries prevent this."""
    resp = client.get("/search?q=" + "' OR '1'='1")
    assert resp.status_code == 200
    data = resp.get_json()
    # The literal string "' OR '1'='1" should not match any item name
    assert data["count"] == 0, (
        "Tautology injection should not return all rows. "
        f"Got {data['count']} results."
    )


def test_sql_injection_comment_out_rest(client):
    """Injection that tries to comment out the rest of the query."""
    resp = client.get("/search?q=" + "Laptop' --")
    assert resp.status_code == 200
    data = resp.get_json()
    # The literal string "Laptop' --" does not exist in the DB
    assert data["count"] == 0, (
        "Comment injection should not bypass parameterisation. "
        f"Got {data['count']} results."
    )


def test_sql_injection_second_order(client):
    """Attempt to inject via a semi-colon (SQLite typically ignores
    multi-statement in execute, but check it doesn't crash)."""
    resp = client.get("/search?q=" + "Laptop; DROP TABLE items; --")
    assert resp.status_code == 200
    data = resp.get_json()
    # The table should still exist — if it were dropped, the next query would fail
    assert "results" in data


def test_sql_injection_blind_boolean(client):
    """Blind boolean injection: ' OR 1=2 -- should return 0 items in a
    vulnerable app only if the injection is evaluated.  Safe apps return 0
    because the literal string doesn't match any product."""
    resp = client.get("/search?q=" + "' OR 1=2 --")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 0


# ── Parameter validation tests ────────────────────────────────


def test_missing_query_returns_400(client):
    """GET /search without ?q= should return 400."""
    resp = client.get("/search")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_empty_query_returns_400(client):
    """GET /search?q=  (empty) should return 400."""
    resp = client.get("/search?q=")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_whitespace_only_query_returns_400(client):
    """GET /search?q=   (whitespace only) should return 400."""
    resp = client.get("/search?q=" + "   ")
    assert resp.status_code == 400


# ── Database integrity test ───────────────────────────────────


def test_database_not_modified_by_injection_attempt(client):
    """After an injection attempt the database must still contain
    the original sample data."""
    # Perform injection
    client.get("/search?q=" + "' OR 1=1 --")

    # Verify all items are still present
    resp = client.get("/items")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["results"]  # non-empty
    names = [r["name"] for r in data["results"]]
    assert "Laptop Pro 15" in names
    assert "Wireless Mouse" in names


# ── Regression tests ──────────────────────────────────────────


def test_special_characters_in_query(client):
    """Percent and underscore are LIKE wildcards — verify the
    endpoint handles them without error and returns expected results."""
    resp = client.get("/search?q=%")
    # '%' alone matches everything via LIKE — so count should be all items
    assert resp.status_code == 200
    data = resp.get_json()
    # All 10 sample items should match '%' since every name has at least 1 char
    assert data["count"] == 10, f"Expected all 10 items, got {data['count']}"

    resp2 = client.get("/search?q=_")
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    # '_' matches every single character — every item name matches
    assert data2["count"] == 10
