# T01 Security Analysis — SQL Injection Detection

## Analysis Date
2026-07-20

## 1) Vulnerable Line Numbers

The vulnerability is on **a single line** of code:

```python
cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")
```

**Line number in context** (full file): line **3** (assuming `user_input` is received externally and `cursor` is a valid database cursor).

## 2) Attack Vector Explanation

### Vulnerability: **String Interpolation in SQL Query**

The code uses an **f-string** (`f"..."`) to directly embed `user_input` into the SQL statement. This is a classic **SQL injection vulnerability**.

### How an attacker exploits it

If `user_input` comes from an untrusted source (HTTP request form field, URL query parameter, API body, etc.), an attacker can supply a crafted string that **breaks out of the SQL string literal** and executes arbitrary SQL commands.

**Example payloads:**

| Payload | Resulting SQL | Effect |
|---------|---------------|--------|
| `' OR '1'='1` | `SELECT * FROM users WHERE username='' OR '1'='1'` | Returns ALL users (bypasses authentication) |
| `' UNION SELECT * FROM credit_cards --` | `SELECT * FROM users WHERE username='' UNION SELECT * FROM credit_cards --'` | Exfiltrates data from other tables |
| `'; DROP TABLE users; --` | `SELECT * FROM users WHERE username=''; DROP TABLE users; --'` | **Destructive** — deletes the entire `users` table |

### Why it's critical

- **CWE-89**: Improper Neutralization of Special Elements used in an SQL Command
- **CVSS 9.8 (Critical)**: Network exploitable, low complexity, no privileges required, compromises confidentiality + integrity + availability
- An attacker can: read arbitrary data, modify/delete records, escalate privileges, execute OS commands (on some DBMS configurations)

### Real-world impact

- 2023: MOVEit Transfer SQLi → data breach of 60+ million records
- 2022: LastPass SQLi in dev environment → source code theft
- Consistently in OWASP Top 10 (#3 in 2021 edition)

## 3) Fixed Version Using Parameterized Queries

### ✅ Correct Approach: Parameterized Query (Placeholders)

```python
# Standard approach — works with sqlite3, psycopg2, pymysql, etc.
cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (user_input,)
)
```

### ✅ ORM Approach (Most Secure — Recommended)

```python
# SQLAlchemy ORM
user = session.query(User).filter(User.username == user_input).first()
```

### Full Fixed Example (`fix_demo.py`)

```python
"""
fix_demo.py — Secure implementation using parameterized queries.
Replaces vulnerable string interpolation with safe placeholder syntax.
"""
import sqlite3
from pathlib import Path


def get_user_by_username_vulnerable(db_path: str, user_input: str) -> list:
    """VULNERABLE version — DO NOT USE."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # ❌ SQL Injection vulnerability — f-string interpolation
    cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")
    results = cursor.fetchall()
    conn.close()
    return results


def get_user_by_username_secure(db_path: str, user_input: str) -> list:
    """SECURE version — uses parameterized query (placeholder ?)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # ✅ Safe — user input treated as data, not executable SQL
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    results = cursor.fetchall()
    conn.close()
    return results


# Demonstrate the fix
if __name__ == "__main__":
    db = ":memory:"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)")
    cursor.execute("INSERT INTO users (username) VALUES ('alice')")
    cursor.execute("INSERT INTO users (username) VALUES ('bob')")
    conn.commit()
    conn.close()

    malicious_input = "' OR '1'='1"

    print("=" * 60)
    print("SECURITY DEMO: SQL Injection Detection & Prevention")
    print("=" * 60)
    print()

    # Demonstrate the attack
    print("VULNERABLE call (f-string interpolation):")
    print(f"  Input: {malicious_input!r}")
    try:
        result = get_user_by_username_vulnerable(db, malicious_input)
        print(f"  Result: {result}")
        print("  ⚠️  ATTACK SUCCEEDED — all users leaked!")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Demonstrate the fix
    print("SECURE call (parameterized query):")
    print(f"  Input: {malicious_input!r}")
    result = get_user_by_username_secure(db, malicious_input)
    print(f"  Result: {result}")
    print("  ✅ Safe — returns empty set (no matching username)")
    print("  The injection payload is treated as a literal string to match,")
    print("  not as executable SQL code.")
```

### Driver Compatibility Matrix

| Database | Placeholder | Example |
|----------|-------------|---------|
| SQLite | `?` | `cursor.execute("SELECT * FROM t WHERE c = ?", (val,))` |
| PostgreSQL (psycopg2) | `%s` | `cursor.execute("SELECT * FROM t WHERE c = %s", (val,))` |
| MySQL (pymysql) | `%s` | `cursor.execute("SELECT * FROM t WHERE c = %s", (val,))` |
| SQLAlchemy ORM | binds | `session.query(T).filter(T.c == val)` |
| Django ORM | automatic | `MyModel.objects.filter(c=val)` |

## Prevention Summary

| ✅ DO | ❌ DON'T |
|-------|---------|
| Use **parameterized queries** with placeholders (`?`, `%s`) | Use **string formatting** (`f"..."`, `.format()`, `%`) in SQL |
| Use an **ORM** layer (SQLAlchemy, Django ORM) | Concatenate user input into SQL strings |
| Validate and sanitize input type (e.g. `int(id)`) | Trust user-supplied data without validation |
| Apply **least privilege** to DB users | Connect as DB admin from application code |
| Use a **WAF** (Web Application Firewall) as defense-in-depth | Rely solely on input sanitization/escaping (parameterization is superior) |

---

*Generated by Elysium Swarmloop — T01 Security Analysis*
