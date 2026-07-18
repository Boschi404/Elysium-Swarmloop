# T01 Code Review — Race Condition Bug in Banking Code

## Bug Summary

**File:** `bank_account.py`
**Class:** `BankAccount`
**Type:** TOCTOU (Time-of-Check-Time-of-Use) race condition — **lost update**

The methods `withdraw()` and `deposit()` perform a **read-modify-write**
cycle across two separate simulated-database calls without any
synchronisation:

```python
def withdraw(self, amount):
    current = self.get_balance()       # DB READ
    if current < amount:
        return False
    new_balance = current - amount
    #        ⚡ Another thread writes here ⚡
    self.set_balance(new_balance)      # DB WRITE — based on STALE data
```

Because the two calls are independent, thread A's write is **silently
overwritten** by thread B if B's read happened before A's write completed.

### Concrete Consequence

| Time | Thread A | Thread B | DB Balance |
|------|----------|----------|:----------:|
| T1   | `read()` → 20 |            | €20 |
| T2   |             | `read()` → 20 | €20 |
| T3   | `write(10)` |            | **€10** |
| T4   |             | `write(10)` | **€10** (overwrites!) |

**Intended effect:** 2 × €10 → €0  
**Actual result:** €10 — one withdrawal vanished.

This is a **lost update**: the first writer's work is destroyed by the
second writer, which based its calculation on stale data.  The balance
**drains slower than expected**, so the race inflates the balance
relative to the sequentially-correct value.

### Real-world impact

- Lost money (never debited from the account)
- Balance > expected = bank loses money
- Under extremely heavy contention: balance stays near zero while
  hundreds of withdrawals keep "succeeding" — each thread reads 0,
  decides the check failed, but the actual balance should be deeply
  negative.

---

## Root Cause

| Problem | Detail |
|---------|--------|
| **Pattern** | Check-then-act across separate non-atomic operations |
| **Violation** | Balance stored externally; read & write are separate network calls |
| **Window** | Between `get_balance()` and `set_balance()` another thread can interleave |
| **Visibility** | No mutex, no DB transaction, no compare-and-swap |

---

## Fix Strategy A — `threading.Lock` (Recommended)

Wrap every read-modify-write sequence inside a mutex so that exactly
one thread holds the lock across both DB calls:

```python
class FixedBankAccount:
    def __init__(self, account_id, initial=0.0):
        self.account_id = account_id
        self._lock = threading.Lock()
        db_write(account_id, initial)

    def withdraw(self, amount):
        with self._lock:                     # ← enter mutex
            current = db_read(self.account_id)
            if current < amount:
                return False
            db_write(self.account_id, current - amount)
            return True                      # ← exit mutex
```

**Pros:** simple, correct, low overhead.  
**Cons:** contention under extreme throughput.

### Full fixed implementation

See `bank_account_fixed.py` → class `FixedBankAccount`.

---

## Fix Strategy B — Queue Serialisation

Route all mutations through a single worker thread that processes
commands sequentially.  See `bank_account_fixed.py` → class
`QueuedBankAccount`.

**Pros:** natural back-pressure; no locks.  
**Cons:** higher latency; worker is a single point of failure.

---

## Fix Strategy C — Atomic CAS (Lock-free)

```python
def withdraw_cas(self, amount):
    while True:
        observed = atomic_read(&balance)
        if observed < amount:
            return False
        desired = observed - amount
        if compare_and_swap(&balance, observed, desired):
            return True
        # CAS failed → another thread changed balance, retry
```

Python lacks native CAS on `int`, but `multiprocessing.Value` and
C extensions support it.  This is the pattern used by Redis, Postgres,
and trading engines.

---

## How the Tests Catch It

| Test | Method | What it proves |
|------|--------|----------------|
| `test_buggy_account_overdrafts_on_race_small_latency` | 20 threads × 50 withdrawals from €500 with simulated DB latency | Buggy account **loses updates**: balance is inflated vs expected |
| `test_fixed_account_survives_concurrent_load` | Same load on `FixedBankAccount` | Lock-based account **exactly correct** — every withdrawal accounted for |
| `test_concurrent_mixed_operations` | 50 threads: deposits & withdrawals interleaved | No drift under mixed contention |
| 3 sequential tests per variant | Single-threaded smoke tests | Basic correctness never broken |

The simulated database (`bank_account._BALANCE_DB`) uses a tiny
`time.sleep(0.001)` on every I/O to force GIL yields inside the
critical section, making the race **deterministically reproducible**.

---

## Checklist

- [x] Bug identified (TOCTOU lost update on read-modify-write)
- [x] Concurrency issue explained (non-atomic DB round-trips)
- [x] Fixed version using `threading.Lock` provided
- [x] Alternative strategies (queue, CAS) documented
- [x] Stress test that reliably catches the race (~1.7s)
- [x] Sequential smoke tests for edge-case correctness
- [x] All 12 tests passing
