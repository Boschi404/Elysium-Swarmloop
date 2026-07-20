"""
fix_demo.py — Secure implementation using parameterized queries.
Replaces vulnerable string interpolation with safe placeholder syntax.

Two versions for comparison:
  - VULNERABLE: f-string interpolation (DO NOT USE)
  - SECURE:     parameterized query with ? placeholder
"""
import sqlite3
import tempfile
import os


DB_PATH = None  # set by main()


def get_user_by_username_vulnerable(user_input: str) -> list:
    """VULNERABLE version — DO NOT USE in production.

    Line: cursor.execute(f"...'{user_input}'")
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ❌ SQL Injection vulnerability — f-string interpolation
    cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")
    results = cursor.fetchall()
    conn.close()
    return results


def get_user_by_username_secure(user_input: str) -> list:
    """SECURE version — uses parameterized query (placeholder ?).

    The DB driver escapes the input correctly, treating it as data only.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ✅ Safe — user input treated as data, not executable SQL
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    results = cursor.fetchall()
    conn.close()
    return results


def setup_db():
    """Seed the shared database with sample users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("INSERT INTO users (username) VALUES ('alice')")
    cursor.execute("INSERT INTO users (username) VALUES ('bob')")
    cursor.execute("INSERT INTO users (username) VALUES ('charlie')")
    conn.commit()
    conn.close()


def main():
    global DB_PATH
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    DB_PATH = tmp.name

    try:
        setup_db()

        # A malicious input that exploits the vulnerability
        malicious_input = "' OR '1'='1"
        legitimate_input = "alice"

        results = []
        failed = 0
        total = 0

        # ── Test 1: Legitimate input with vulnerable version ──
        print("Test 1 | Legitimate input | VULNERABLE version")
        total += 1
        result = get_user_by_username_vulnerable(legitimate_input)
        print(f"        Input: {legitimate_input!r}")
        print(f"        Result: {result}")
        if len(result) == 1 and result[0][1] == "alice":
            print(f"        ✅ PASS — returns {'alice'!r}")
        else:
            print(f"        ❌ FAIL — expected [alice]")
            failed += 1
        print()

        # ── Test 2: Legitimate input with secure version ──
        print("Test 2 | Legitimate input | SECURE version")
        total += 1
        result = get_user_by_username_secure(legitimate_input)
        print(f"        Input: {legitimate_input!r}")
        print(f"        Result: {result}")
        if len(result) == 1 and result[0][1] == "alice":
            print(f"        ✅ PASS — returns {'alice'!r}")
        else:
            print(f"        ❌ FAIL — expected [alice]")
            failed += 1
        print()

        # ── Test 3: Malicious input with vulnerable version ──
        print("Test 3 | Malicious input  | VULNERABLE version")
        total += 1
        result = get_user_by_username_vulnerable(malicious_input)
        print(f"        Input: {malicious_input!r}")
        print(f"        Result: {result}")
        if len(result) == 3:
            print(f"        ⚠️  VULNERABLE — SQL injection leaks ALL users!")
            print(f"        ❌ FAIL — should return empty")
            failed += 1
        else:
            print(f"        ✅ PASS")
        print()

        # ── Test 4: Malicious input with secure version ──
        print("Test 4 | Malicious input  | SECURE version")
        total += 1
        result = get_user_by_username_secure(malicious_input)
        print(f"        Input: {malicious_input!r}")
        print(f"        Result: {result}")
        if len(result) == 0:
            print(f"        ✅ PASS — injection neutralised (empty result set)")
        else:
            print(f"        ❌ FAIL — expected empty list")
            failed += 1
        print()

        # ── Summary ──
        print("=" * 60)
        print(f"RESULTS: {total - failed}/{total} passed")
        if failed:
            print(f"⚠️  {failed} test(s) failed — review vulnerabilities above")
        else:
            print("✅ ALL TESTS PASSED — fix is verified")
        print("=" * 60)

    finally:
        os.unlink(DB_PATH)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
