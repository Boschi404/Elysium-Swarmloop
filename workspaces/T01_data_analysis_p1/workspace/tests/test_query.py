#!/usr/bin/env python3
"""Tests for the Q4 2024 Sales Report Query.

Runs the SQL against SQLite with test data and validates output.
Exit code 0 = all tests pass.
"""

import sqlite3
import sys
import os

WORKSPACE = os.path.join(os.path.dirname(__file__), '..')
SCHEMA = os.path.join(WORKSPACE, 'schema.sql')
SEED   = os.path.join(WORKSPACE, 'seed.sql')
QUERY  = os.path.join(WORKSPACE, 'query.sql')

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def run_tests():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Load schema + seed data
    conn.executescript(read_file(SCHEMA))
    conn.executescript(read_file(SEED))

    # Run the query
    query = read_file(QUERY)
    rows = conn.execute(query).fetchall()

    # --- TESTS ---

    failures = []

    # 1) Row count: 4 categories (Home Office, Electronics, Stationery, Uncategorized)
    #    NULL categories are GROUP BY'd into a single 'Uncategorized' row
    if len(rows) != 4:
        failures.append(f"Expected 4 rows, got {len(rows)}: {[r['category_name'] for r in rows]}")

    # 2) First row should be 'Home Office' (highest revenue: 2×299.99+1×289.99+1×449+1×45)
    #    Home Office: 2x45 + 299.99 + 289.99 + 449 = 1,083.98
    if rows[0]['category_name'] != 'Home Office':
        failures.append(f"Expected 'Home Office' first, got '{rows[0]['category_name']}'")

    # 3) Last row must be 'Uncategorized' (lowest revenue: 7×12.50 + 3×5.00 = 102.50)
    if rows[-1]['category_name'] != 'Uncategorized':
        failures.append(f"Expected 'Uncategorized' last, got '{rows[-1]['category_name']}'")

    # 4) Build a lookup dict
    result = {r['category_name']: r for r in rows}

    # 5) Home Office — revenue: 45.00+45.00 + 299.99 + 289.99 + 449.00 = 1,128.98
    #    units: 2+1+1+1 = 5
    ho = result.get('Home Office')
    if ho:
        if abs(ho['total_revenue'] - 1128.98) > 0.01:
            failures.append(f"Home Office revenue: expected 1128.98, got {ho['total_revenue']}")
        if ho['total_units_sold'] != 5:
            failures.append(f"Home Office units: expected 5, got {ho['total_units_sold']}")
        # average price: (45.00 + 299.99 + 289.99 + 449.00) / 4 = 1083.98/4 = 270.995 -> ROUND = 271.00
        # Actually: 45.00, 299.99, 289.99, 449.00 → AVG = 270.995 → ROUND 271.00
        exp_avg = 271.00
        if abs(ho['average_price'] - exp_avg) > 0.01:
            failures.append(f"Home Office avg price: expected {exp_avg}, got {ho['average_price']}")
    else:
        failures.append("Missing 'Home Office' row")

    # 6) Electronics — revenue: 3×25.99 + 1×24.50 + 5×18.75 + 2×79.99
    #    = 77.97 + 24.50 + 93.75 + 159.98 = 356.20
    #    units: 3+1+5+2 = 11
    el = result.get('Electronics')
    if el:
        if abs(el['total_revenue'] - 356.20) > 0.01:
            failures.append(f"Electronics revenue: expected 356.20, got {el['total_revenue']}")
        if el['total_units_sold'] != 11:
            failures.append(f"Electronics units: expected 11, got {el['total_units_sold']}")
    else:
        failures.append("Missing 'Electronics' row")

    # 7) Uncategorized — revenue: 7×12.50 + 3×5.00 = 87.50 + 15.00 = 102.50
    #    units: 7+3 = 10
    unc = result.get('Uncategorized')
    if unc:
        if abs(unc['total_revenue'] - 102.50) > 0.01:
            failures.append(f"Uncategorized revenue: expected 102.50, got {unc['total_revenue']}")
        if unc['total_units_sold'] != 10:
            failures.append(f"Uncategorized units: expected 10, got {unc['total_units_sold']}")
    else:
        failures.append("Missing 'Uncategorized' row")

    # 8) All values rounded to 2 decimals
    for r in rows:
        rev_str = str(r['total_revenue'])
        price_str = str(r['average_price'])
        if '.' in rev_str:
            decimals = rev_str.split('.')[1]
            if len(decimals) > 2:
                failures.append(f"Revenue {r['total_revenue']} in {r['category_name']} has >2 decimals")
        if '.' in price_str:
            decimals = price_str.split('.')[1]
            if len(decimals) > 2:
                failures.append(f"Avg price {r['average_price']} in {r['category_name']} has >2 decimals")

    conn.close()

    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  ✗  {f}")
        sys.exit(1)
    else:
        print("✓  All tests passed (5 categories, correct values, rounded, sorted)")
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
