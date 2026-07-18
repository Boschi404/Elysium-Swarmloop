# Code Review: Race Condition Bug in Banking Code

## Solution

### Bug Identification

The bug is a **classic read-modify-write race condition** in `BuggyBankAccount`. The methods `deposit()` and `withdraw()` follow this non-atomic pattern:

```python
current = self.get_balance()     # read
new_balance = current +/- amount  # modify
self.set_balance(new_balance)     # write
```

When two threads execute this sequence concurrently, their reads and writes interleave, causing **lost updates**. The race window is widened by the artificial `time.sleep(0.001)` inside `set_balance()`.

### Concurrency Explanation

The core issue is the **check-then-act** pattern and the **read-modify-write** being split across three operations without mutual exclusion. In Python's CPython, the GIL protects individual bytecode instructions but does **not** protect multi-statement critical sections. Between `get_balance()` and `set_balance()`, a thread switch can occur, leaving both threads operating on stale data.

**Race scenario (two threads, initial balance 100):**

```
Thread A                           Thread B
───────────                       ───────────
current = get_balance()  → 100
                                   current = get_balance()  → 100  ← STALE!
current -= 30            → 70
                                   current -= 50            → 50
set_balance(70)          → 70
                                   set_balance(50)          → 50  ← A's update LOST!
```

**Correct result**: 100 - 30 - 50 = **20**
**Actual result with race**: **50** or **70** (last writer wins)

This is the textbook **lost update** problem — both threads read the same initial value, each computes their new balance, and the last one to write obliterates the other's update.

### Fix: threading.Lock

The fix wraps every critical section in a `threading.Lock` via the context manager (`with self._lock:`). This guarantees **mutual exclusion**: only one thread can execute the read-check-write sequence at a time.

```python
class LockedBankAccount:
    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance
        self._lock = threading.Lock()

    def withdraw(self, amount: float) -> bool:
        if amount < 0:
            raise ValueError("Withdrawal amount must be non-negative")
        with self._lock:                    # ← ENTER MUTEX
            if self._balance < amount:       # check (protected)
                return False
            new_balance = self._balance - amount
            self._balance = new_balance      # write (protected)
            return True                      # ← EXIT MUTEX
```

Key points of the fix:
- **Single lock acquisition**: read, check, and write happen under one `with self._lock:` block — no interleaving possible.
- **Context manager**: guarantees `lock.release()` even if an exception is raised.
- **No performance bottleneck for realistic workloads**: lock contention is negligible for bank-account-style operations; Python's `threading.Lock` is fast (microseconds).

### Alternative Approaches

| Approach | Mechanism | Use Case |
|----------|-----------|----------|
| `threading.Lock` | Mutual exclusion on critical section | General-purpose, simple |
| `threading.RLock` | Re-entrant lock (same thread can re-acquire) | When public methods call each other |
| `queue.Queue` | Serialize all operations through a single worker thread | Actor model / single-writer pattern |
| `threading.atomic` via `compare-and-swap` | CAS wrapped in a lock (see `AtomicBankAccount`) | Higher-level operation abstraction |
| Database transaction | `UPDATE accounts SET balance = balance - 50 WHERE id = X` | When state lives in a DB |

For pure Python single-process code, `threading.Lock` is the recommended fix — minimal overhead, maximal clarity, and well-understood semantics.

## Test That Catches This Bug

The test file `tests/test_bank.py` contains three test classes:

1. **`TestBuggyBankSingleThread`** (6 tests) — single-threaded correctness. Even the buggy bank passes these, confirming the bug is purely a concurrency issue.

2. **`TestRaceCondition`** (2 tests) — the critical test:
   - `test_buggy_bank_has_race_condition()`: launches 10 threads, each withdrawing 10 from a 100 balance. The buggy bank **fails** (final balance ≠ 0) because of lost updates. **This assertion proves the race condition exists.**
   - `test_locked_bank_prevents_race()`: same workload on the fixed bank. **Passes** (balance == 0), proving the lock serialises correctly.

3. **`TestDeterministicRace`** (1 test) — uses a `threading.Barrier` to force both threads to read the balance before either writes. No timing dependency: the interleaving is guaranteed to produce the race. **This proves the lost-update bug deterministically.**

4. **`TestFixedBankStress`** (2 tests) — high-volume stress tests (500+ operations across 50 threads) confirming the lock holds up under pressure.

### Running the Tests

```bash
cd workspaces/T01_code_review_p5/workspace
python -m pytest tests/ -v
```

## Edge Cases Considered

- **Insufficient funds**: `withdraw()` returns `False` and balance unchanged (tested).
- **Negative amounts**: both `deposit()` and `withdraw()` raise `ValueError` (tested).
- **Zero balance**: withdraw from zero returns `False`.
- **Concurrent deposits only**: all sums are preserved (tested via stress test).
- **Balanced deposits + withdrawals**: final balance equals initial (tested via stress test).

## Summary

| Aspect | Detail |
|--------|--------|
| **Bug type** | Race condition (lost update) in read-modify-write pattern |
| **Root cause** | `get_balance()` and `set_balance()` called separately without a mutex |
| **Fix** | Wrap the critical section in `with self._lock:` |
| **Consequence of bug** | Silent corruption — balance is wrong, but no exception is raised |
| **How to reproduce** | Run 10 concurrent withdrawals on 100 balance; expect balance ≠ 0 |
| **Difficulty** | 4/10 — classic concurrency bug, easy to miss without multi-threaded testing |
