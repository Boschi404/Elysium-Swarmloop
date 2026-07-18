"""
Test suite for sales_report_q4_2024.sql

Creates an in-memory SQLite database with sample data,
runs the query, and validates the output meets requirements.
"""
import sqlite3
import pathlib
import sys

TEST_DIR = pathlib.Path(__file__).parent
WORKSPACE = TEST_DIR.parent
QUERY_FILE = WORKSPACE / "queries" / "sales_report_q4_2024.sql"
SEED = 42  # deterministic random sample


def _create_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT
        );

        CREATE TABLE sales (
            sale_id    INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(product_id),
            amount     REAL    NOT NULL,
            sale_date  TEXT    NOT NULL  -- ISO-8601 date
        );
    """)


def _seed_data(conn: sqlite3.Connection):
    import random
    rng = random.Random(SEED)

    # ---- products (10 rows) ----
    categories = ["Electronics", "Clothing", "Home", "Books", None,
                  "Electronics", "Clothing", "Home", "Books", "Sports"]
    names = [
        "Laptop", "T-Shirt", "Sofa", "Novel", "Widget",
        "Phone", "Jeans", "Lamp", "Guide", "Soccer Ball",
    ]
    conn.executemany(
        "INSERT INTO products (product_id, product_name, category) VALUES (?, ?, ?)",
        [(i, names[i], categories[i]) for i in range(10)],
    )

    # ---- sales (200+ rows across Q3 and Q4 2024) ----
    # Mix of Q3 (should be excluded) and Q4 (should be included)
    dates_q3 = ["2024-09-{:02d}".format(d) for d in range(1, 31)]
    dates_q4 = ["2024-10-{:02d}".format(d) for d in range(1, 32)]
    dates_q4 += ["2024-11-{:02d}".format(d) for d in range(1, 31)]
    dates_q4 += ["2024-12-{:02d}".format(d) for d in range(1, 32)]

    all_dates = dates_q3 + dates_q4
    rng.shuffle(all_dates)

    amounts = []  # (date, product_id, amount)
    for d in all_dates:
        pid = rng.randint(0, 9)
        amt = round(rng.uniform(5.0, 2500.0), 2)
        amounts.append((d, pid, amt))

    conn.executemany(
        "INSERT INTO sales (sale_date, product_id, amount) VALUES (?, ?, ?)",
        amounts,
    )
    conn.commit()


def _read_query() -> str:
    return QUERY_FILE.read_text(encoding="utf-8")


def _run_query(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cur = conn.execute(_read_query())
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_query_executes():
    """The SQL query must parse and run without errors."""
    conn = sqlite3.connect(":memory:")
    _create_schema(conn)
    _seed_data(conn)
    rows = _run_query(conn)
    assert len(rows) > 0, "Query returned zero rows"
    conn.close()


def test_columns_present():
    """Result must include all four required columns."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    _seed_data(conn)
    rows = _run_query(conn)
    col_names = [d[0].lower() for d in conn.execute(_read_query()).description]
    for expected in ("category_name", "total_units_sold", "total_revenue", "avg_price"):
        assert expected in col_names, f"Missing column: {expected}"
    conn.close()


def test_uncategorized_handling():
    """NULL categories must appear as 'Uncategorized'."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    # Insert just a NULL-category product + one sale
    conn.execute("INSERT INTO products (product_id, product_name, category) VALUES (1, 'Widget', NULL)")
    conn.execute("INSERT INTO sales (sale_id, product_id, amount, sale_date) VALUES (1, 1, 100.00, '2024-10-15')")
    rows = _run_query(conn)
    names = [r["category_name"] for r in rows]
    assert "Uncategorized" in names, f"Expected 'Uncategorized' in {names}"
    conn.close()


def test_q4_only():
    """Only dates in Q4 2024 (Oct-Dec) are included."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    conn.execute("INSERT INTO products (product_id, product_name, category) VALUES (1, 'A', 'Test')")
    conn.execute("INSERT INTO sales (sale_id, product_id, amount, sale_date) VALUES (1, 1, 10, '2024-09-30')")  # Q3
    conn.execute("INSERT INTO sales (sale_id, product_id, amount, sale_date) VALUES (2, 1, 20, '2024-10-01')")  # Q4
    rows = _run_query(conn)
    assert len(rows) == 1, f"Expected 1 row (Q4 only), got {len(rows)}"
    assert rows[0]["total_revenue"] == 20.0, f"Expected revenue 20.0, got {rows[0]['total_revenue']}"
    conn.close()


def test_revenue_desc_sort():
    """Results are sorted by total_revenue descending."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    conn.execute("INSERT INTO products (product_id, product_name, category) VALUES (1, 'A', 'Low'), (2, 'B', 'High')")
    conn.execute("INSERT INTO sales (sale_id, product_id, amount, sale_date) VALUES "
                 "(1, 1, 5, '2024-10-01'),"
                 "(2, 2, 50, '2024-10-01')")
    rows = _run_query(conn)
    revenues = [r["total_revenue"] for r in rows]
    assert revenues == sorted(revenues, reverse=True), f"Not sorted descending: {revenues}"
    conn.close()


def test_rounding():
    """Revenue and avg_price are rounded to 2 decimals."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    conn.execute("INSERT INTO products (product_id, product_name, category) VALUES (1, 'A', 'Test')")
    conn.execute("INSERT INTO sales (sale_id, product_id, amount, sale_date) VALUES "
                 "(1, 1, 10.456, '2024-10-01'),"
                 "(2, 1, 20.784, '2024-10-01')")
    rows = _run_query(conn)
    r = rows[0]
    # 10.456 + 20.784 = 31.24; avg = 15.62
    assert r["total_revenue"] == 31.24, f"Expected 31.24, got {r['total_revenue']}"
    assert r["avg_price"] == 15.62, f"Expected 15.62, got {r['avg_price']}"
    conn.close()


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import inspect
    this_module = sys.modules[__name__]
    tests = [
        obj for name, obj in inspect.getmembers(this_module)
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{'=' * 40}")
    print(f"  {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(0 if failed == 0 else 1)
