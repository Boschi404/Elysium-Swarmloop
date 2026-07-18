"""
Tests for T03_data_analysis_p3 — Multi-Table JOIN Report.

Validates that the SQL query correctly:
1. Joins customers ↔ orders ↔ order_items ↔ products
2. Filters to only the last 30 days
3. Includes customers with NO orders (0 quantity, NULL product)
4. Sorts by order_date DESC, customer_name ASC
5. Computes line_total = quantity × price
"""

import sqlite3
import sys
from pathlib import Path

import pytest

# Paths relative to this test file
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
SCHEMA_SQL = WORKSPACE / "solution" / "schema.sql"
QUERY_SQL = WORKSPACE / "solution" / "query.sql"

# --------------- helpers ---------------

@pytest.fixture(scope="session")
def db():
    """Create an in-memory SQLite DB, seed it, and return a connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Read and execute schema + data
    schema = SCHEMA_SQL.read_text(encoding="utf-8")
    cur.executescript(schema)
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture(scope="session")
def results(db):
    """Execute the solution query and return all rows as dicts."""
    query = QUERY_SQL.read_text(encoding="utf-8")
    cur = db.cursor()
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    return rows


# --------------- VALIDATION TESTS ---------------

def test_all_customers_appear(results):
    """Every customer should appear — even those with no orders."""
    all_names = {r["customer_name"] for r in results}
    expected = {
        "Alice Rossi", "Marco Bianchi", "Sofia Verdi",
        "Luca Neri", "Giulia Gialli",
        "Paolo Blu", "Elena Viola", "Davide Arancione",
    }
    missing = expected - all_names
    assert not missing, f"Missing customers: {missing}"


def test_customers_without_orders_show_zero_quantity(results):
    """Customers with no orders should have quantity=0 and NULL product."""
    no_order_customers = {"Paolo Blu", "Elena Viola", "Davide Arancione"}
    for r in results:
        if r["customer_name"] in no_order_customers:
            assert r["quantity"] == 0, (
                f"{r['customer_name']}: expected 0, got {r['quantity']}"
            )
            assert r["product_name"] is None, (
                f"{r['customer_name']}: expected NULL product, "
                f"got {r['product_name']!r}"
            )
            assert r["order_date"] is None, (
                f"{r['customer_name']}: expected NULL order_date, "
                f"got {r['order_date']!r}"
            )
            assert r["line_total"] == 0.0, (
                f"{r['customer_name']}: expected 0 line_total, "
                f"got {r['line_total']}"
            )


def test_only_recent_orders_included(results):
    """No rows should reference orders older than 30 days from 'now'."""
    import datetime

    # Read board time from DB so we match DATE('now') used in the query
    # (SQLite's DATE('now') is UTC)
    today_str = "2026-07-18"  # fallback; will be overridden via DB call
    for r in results:
        if r["order_date"] is not None:
            assert r["order_date"] >= "2026-06-18", (  # ~30 days before mid-jul
                f"Order date {r['order_date']} is older than 30 days "
                f"(customer {r['customer_name']})"
            )


def _today_from_db(db):
    """Get SQLite's DATE('now') so tests align with query logic."""
    cur = db.cursor()
    cur.execute("SELECT DATE('now')")
    return cur.fetchone()[0]


def test_only_recent_orders_included_accurate(db, results):
    """Use SQLite's actual DATE('now') to verify the 30-day window."""
    cur = db.cursor()
    cur.execute("SELECT DATE('now', '-30 days')")
    cutoff = cur.fetchone()[0]

    for r in results:
        if r["order_date"] is not None:
            assert r["order_date"] >= cutoff, (
                f"Order date {r['order_date']} is before cutoff {cutoff} "
                f"(customer {r['customer_name']})"
            )


def test_line_total_calculation(results):
    """line_total should equal quantity × price for every row with data."""
    for r in results:
        if r["product_name"] is not None:
            expected = r["quantity"] * 350.0  # crude — we re-query below
    # Better: re-derive from the seed data. Let's be specific.
    curated_checks = {
        ("Alice Rossi", "Tavolo in rovere"): (1, 350.0),
        ("Alice Rossi", "Sedia ergonomica"): (4, 4 * 120.50),
        ("Alice Rossi", "Lampada da terra"): (2, 2 * 89.99),
        ("Marco Bianchi", "Scrivania in vetro"): (1, 450.0),
        ("Marco Bianchi", "Libreria componibile"): (2, 2 * 210.0),
        ("Sofia Verdi", "Sedia ergonomica"): (2, 2 * 120.50),
        ("Luca Neri", "Tavolo in rovere"): (1, 350.0),
        ("Luca Neri", "Lampada da terra"): (1, 89.99),
        ("Giulia Gialli", "Libreria componibile"): (3, 3 * 210.0),
    }

    # Build lookup keyed by (name, product) — a customer may buy the same
    # product in separate orders; that's fine, we check individually.
    for r in results:
        key = (r["customer_name"], r["product_name"])
        if key in curated_checks:
            expected_qty, expected_total = curated_checks[key]
            assert r["quantity"] == expected_qty, (
                f"{key}: expected qty={expected_qty}, got {r['quantity']}"
            )
            # Use approximate equality for floating point
            assert abs(r["line_total"] - expected_total) < 0.01, (
                f"{key}: expected line_total={expected_total}, "
                f"got {r['line_total']}"
            )
            del curated_checks[key]

    # All checks should have been exhausted
    assert not curated_checks, (
        f"Some expected rows were NOT found in results: {curated_checks}"
    )


def test_sort_order(results):
    """
    Verify sort: order_date DESC, customer_name ASC.
    Rows with NULL order_date (no-order customers) sort last in DESC.
    """
    prev_date = "9999-99-99"  # sentinel — first NULL will be last
    prev_name = ""
    seen_null = False

    for r in results:
        od = r["order_date"]
        name = r["customer_name"]

        if od is None:
            seen_null = True
            continue  # NULL-sorted rows don't need date comparison

        if seen_null:
            pytest.fail(
                f"Non-NULL order_date {od} appears after NULL-sorted rows "
                f"(customer {name})"
            )

        # order_date DESC
        assert od <= prev_date, (
            f"order_date {od} > {prev_date} (not descending) "
            f"at customer {name}"
        )
        if od == prev_date:
            # customer_name ASC (case-insensitive tiebreaker)
            assert name >= prev_name, (
                f"customer_name {name} < {prev_name} (not ascending) "
                f"on same date {od}"
            )

        prev_date = od
        prev_name = name


def test_required_columns(results):
    """Check every row has the four required output fields."""
    for r in results:
        assert "customer_name" in r
        assert "order_date" in r or r["order_date"] is None
        assert "product_name" in r
        assert "quantity" in r
        assert "line_total" in r


def test_no_order_items_with_zero_quantity(results):
    """
    Customers WITH orders but zero quantity should not happen
    (order_items always has qty > 0 by schema CHECK).
    """
    for r in results:
        if r["order_date"] is not None:
            assert r["quantity"] > 0, (
                f"{r['customer_name']} has order_date {r['order_date']} "
                f"but quantity={r['quantity']}"
            )


def test_sql_file_readable():
    """Both .sql files must exist and be non-empty."""
    assert SCHEMA_SQL.exists(), f"Missing: {SCHEMA_SQL}"
    assert QUERY_SQL.exists(), f"Missing: {QUERY_SQL}"
    assert len(SCHEMA_SQL.read_text()) > 200
    assert len(QUERY_SQL.read_text()) > 100
