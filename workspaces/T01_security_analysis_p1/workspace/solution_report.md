# T01 Security Analysis — SQL Injection Detection

## Code Under Review

```python
cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")
```

---

## 1) Vulnerable Line Number

**Line 1** — the single line passed for review. Every part of this line is vulnerable due to f-string interpolation of user-controlled input directly into the SQL statement.

---

## 2) Attack Vector Explanation

**SQL Injection** occurs because user-supplied input (`user_input`) is concatenated into the SQL query via an f-string **before** the query is sent to the database engine.

### How an attacker exploits it:

An attacker provides crafted input that **breaks out of the string literal** and injects arbitrary SQL clauses.

| Input | Resulting SQL | Effect |
|-------|--------------|--------|
| `' OR '1'='1` | `SELECT * FROM users WHERE username='' OR '1'='1'` | Returns **all users** — authentication bypass |
| `' UNION SELECT * FROM credit_cards--` | `SELECT * FROM users WHERE username='' UNION SELECT * FROM credit_cards--'` | Data exfiltration from other tables |
| `'; DROP TABLE users;--` | `SELECT * FROM users WHERE username=''; DROP TABLE users;--'` | **Destructive** — table deletion |

### Why this is dangerous:

- The **database cannot distinguish** between code and data in an f-string context — the query string is already fully formed by the time it reaches `cursor.execute()`.
- The attacker controls arbitrary SQL syntax, not just the value of `username`.
- Even a **single quote** (`'`) breaks the query structure.

---

## 3) Fixed Version

### Fix A: Parameterized Query (Recommended)

```python
# Safe — user input bound as data, never parsed as SQL code
cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (user_input,)
)
```

**Mechanism:** The `?` placeholder tells the database driver to treat `user_input` **exclusively as a data value**. The database engine compiles the query structure first, then safely binds the input — no escape can produce malicious SQL because the SQL grammar is already fixed.

### Fix B: Named Placeholders (SQLite / psycopg2)

```python
cursor.execute(
    "SELECT * FROM users WHERE username = :username",
    {"username": user_input}
)
```

### Fix C: `%s` style (MySQL Connector / psycopg2)

```python
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (user_input,)
)
```

---

## Verification Checklist

| Check | Result |
|-------|--------|
| Original code vulnerable? | ✅ Yes |
| Parameterized query used? | ✅ Yes |
| Placeholder (`?`, `%s`, `:name`) in SQL string | ✅ Yes |
| User input passed separately (tuple/dict) | ✅ Yes |
| No string formatting/concatenation in SQL | ✅ Yes |

---

## Key Takeaway

> **Never** build SQL queries with string interpolation (`f"..."`, `.format()`, `+`) when user input is involved. Always use **parameterized queries** (placeholders + separate data). This completely prevents SQL injection — the database engine treats input as data, never as executable SQL code.
