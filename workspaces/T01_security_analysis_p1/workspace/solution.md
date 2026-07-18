# T01 Security Analysis — SQL Injection Detection

## Solution

### 1) Vulnerable Line Numbers — Identify the Weakness

The vulnerability is on **line 1** of the given code. I identify the f-string pattern as the root cause:

```python
cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")
```

Every line that constructs SQL queries using f-strings (`f"..."`) with unsanitized user input is vulnerable. In this case, the entire `cursor.execute(...)` call is the vulnerable statement.

### 2) Attack Vector Explanation

This is a **classic SQL injection** vulnerability. I will explain the mechanics concisely: the f-string interpolates `user_input` directly into the SQL query string without any escaping, validation, or parameterization.

**How an attacker exploits it:**

If an attacker provides `user_input` containing SQL metacharacters, they can break out of the intended query context and execute arbitrary SQL.

**Example attack payloads:**

| Payload | Resulting Query | Effect |
|---------|----------------|--------|
| `' OR '1'='1` | `SELECT * FROM users WHERE username='' OR '1'='1'` | Returns **all** users (authentication bypass) |
| `'; DROP TABLE users; --` | `SELECT * FROM users WHERE username=''; DROP TABLE users; --'` | **Destructive** — deletes the entire `users` table |
| `' UNION SELECT password FROM admins; --` | `SELECT * FROM users WHERE username='' UNION SELECT password FROM admins; --'` | **Data exfiltration** — leaks passwords from another table |
| `admin' OR '1'='1' --` | `SELECT * FROM users WHERE username='admin' OR '1'='1' --'` | Logs in as `admin` without knowing the password |

**Root cause:** The code treats `user_input` as trusted data when it should be treated as untrusted. String interpolation (`f"..."`) concatenates the user-supplied text directly into the SQL grammar, allowing the attacker to change the query's structure.

**Edge case:** Even when `user_input` looks benign (e.g., a simple username), special characters like single quotes (`'`), backslashes (`\`), or control characters can break the query or enable second-order injection if the data is later used unsafely.

### 3) Fixed Version Using Parameterized Queries

The secure approach uses **parameterized queries** (also called prepared statements). The database driver handles escaping and ensures user input is never interpreted as SQL syntax.

```python
# SECURE FIX — parameterized query with placeholder
cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (user_input,)
)
```

**Why this works:**

- The `?` placeholder marks where user data goes
- The database driver sends the parameter **separately** from the SQL structure
- Even if `user_input` contains `' OR '1'='1`, it is treated as a **literal string value**, not SQL code
- The database engine compiles the query structure first, then safely binds the parameter

**Alternative syntax for different databases:**

| Database | Placeholder | Example |
|----------|-------------|---------|
| SQLite | `?` | `cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))` |
| PostgreSQL (psycopg2) | `%s` | `cursor.execute("SELECT * FROM users WHERE username = %s", (user_input,))` |
| MySQL (mysql-connector) | `%s` | `cursor.execute("SELECT * FROM users WHERE username = %s", (user_input,))` |
| SQLAlchemy ORM | n/a | `session.query(User).filter(User.username == user_input).all()` |

**Defense in depth — additional recommendations:**

1. **Least privilege:** The database user should have only `SELECT` permissions for read queries — even if injection occurs, damage is limited.
2. **Input validation:** Validate `user_input` format (e.g., alphanumeric-only for usernames) as a secondary defense.
3. **ORMs preferred:** Use SQLAlchemy or Django ORM which abstract raw SQL and eliminate manual query construction.
4. **Static analysis:** Run `bandit` or `semgrep` in CI to catch f-string SQL patterns automatically.

### Summary

The single line `cursor.execute(f"SELECT * FROM users WHERE username='{user_input}'")` is vulnerable to SQL injection. **Parameterized queries** are the definitive fix — they separate SQL structure from user data, making injection structurally impossible.
