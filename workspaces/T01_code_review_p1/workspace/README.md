# T01_code_review — Race Condition Bug in Banking Code

## The Bug

**File:** `bank_account.py` → method `BankAccount.withdraw()`

```python
def withdraw(self, amount: float) -> bool:
    current = self.get_balance()    # ✅ READ
    if current < amount:
        return False
    new_balance = current - amount  # 🔸 MODIFY (local var only)
    self.set_balance(new_balance)   # ❌ WRITE
    return True
```

This is a **classic read-modify-write race condition** (also known as TOCTOU — Time-of-Check to Time-of-Use).

## Concurrency Issue

When two threads (or processes) call `withdraw()` on the **same account** concurrently, the interleaving can produce a **lost update**:

```
Time  Thread-1                  Thread-2                  Balance
───   ────────                  ────────                  ───────
T0    get_balance() → 100                                 $100
T1                              get_balance() → 100       $100
T2    100 - 50 = 50                                        (local)
T3                             100 - 30 = 70               (local)
T4    set_balance(50)                                      $50
T5                              set_balance(70)            $70  ← WRONG!
```

**Result:** Thread-1's withdrawal of €50 **disappears** — the final balance is €70 instead of the correct €20 (100 − 50 − 30). The customer just lost €50.

### Real-world impact

- Lost transactions in payment processing
- Overdrawn accounts without detection
- Double-spending in any ledger system
- Corrupted audit trails

## The Fix

**File:** `bank_account_fixed.py` — uses `threading.Lock` to serialise the critical section:

```python
def withdraw(self, amount: float) -> bool:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    with self._lock:                         # ← atomic block
        if self._balance < amount:
            return False
        self._balance -= amount              # read + check + write = atomic
    return True
```

### Alternative fixes (depending on context)

| Approach | When to use |
|----------|-------------|
| `threading.Lock` | Single-process, multi-threaded applications |
| `threading.RLock` | Methods that call each other recursively |
| `queue.Queue` | Producer-consumer patterns (one worker at a time) |
| Atomic DB update (`UPDATE account SET balance = balance - ? WHERE balance >= ?`) | Real banking / multi-process systems |
| `redis-py` optimistic locking (WATCH/MULTI/EXEC) | Distributed systems |

## Test That Catches the Bug

**File:** `tests/test_race_condition.py`

The test spawns N concurrent threads that each withdraw €10 from an account with initial balance €100. With the buggy version, the final balance is **almost never correct** (expect €0, usually see €30–€70 due to lost updates). With the fixed version, the balance is **always exactly €0**.

## Reproduction Steps

```bash
cd workspace
pytest tests/ -v
```

The buggy test will fail on most runs (non-deterministic — the race is easiest to reproduce on multi-core machines or with GIL-released Python builds).
