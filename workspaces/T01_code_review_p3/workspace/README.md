# T01 — Code Review: Race Condition Bug

## The Bug

File: `bank_account.py`

Every mutating method (`deposit`, `withdraw`, `transfer_to`) follows this unsafe
pattern:

```python
current = self.balance       # READ
new_balance = current + amount
self.balance = new_balance   # WRITE
```

This is a classic **TOCTOU** (Time Of Check, Time Of Use) race condition.  The
balance is read into a local variable, a computation is performed, and then the
result is written back — but nothing prevents another thread from interleaving a
write **between** the read and the write.

### What can go wrong

Two threads each deposit 100 into an account with balance 0:

```
Time   Thread-A          Thread-B          Balance
─────  ────────────────  ────────────────  ───────
  1    read balance → 0                      0
  2                     read balance → 0      0
  3    write 0+100=100                       100
  4                     write 0+100=100      100   ← Thread-B's update LOST
```

Expected final balance: 200.  Actual: 100.  The deposit from Thread-B is
silently lost — no error, no exception, just corrupted state.

The same pattern affects `withdraw` (missing withdrawals) and can even bypass
the insufficient-funds check (two threads both pass the `if current < amount`
guard before either writes).

## The Fix

File: `bank_account_fixed.py`

Wrap every read-modify-write in a **reentrant lock** (`threading.RLock`):

```python
with self._lock:
    self._balance += amount      # atomic read-modify-write
```

Why `RLock` (reentrant) instead of `Lock`?  Because `transfer_to` calls
`withdraw` + `deposit` internally — a reentrant lock lets the same thread
acquire it multiple times without deadlocking.

### Transfer deadlock prevention

For `transfer_to` the naive lock-both approach can deadlock when A→B and B→A
happen simultaneously.  The fix acquires locks in a fixed order (source first,
then target), or as done here uses a single lock per transfer to keep it simple
while remaining safe.

## The Test

File: `tests/test_bank_account.py`

The test uses a **Barrier** (`threading.Barrier`) so that N threads all hit the
critical section at the **same instant**, making the race condition reproducible
on every run — not a flaky intermittent test.

| Test | What it proves |
|------|----------------|
| `test_race_condition_deposit_detected` | 50 concurrent deposits on buggy account → lost updates |
| `test_race_condition_withdraw_detected` | 50 concurrent withdrawals → lost updates |
| `test_fixed_version_no_race_deposits` | Same load on fixed account → correct balance |
| `test_fixed_version_no_race_withdrawals` | Same load on fixed account → correct balance |
| `test_fixed_version_negative_balance_prevented` | 3 withdrawals of 40 from 50 → at most 1 succeeds |
| `test_mixed_concurrent_workload` | Interleaved deposits & withdrawals → correct balance |

The buggy version test will **fail** (expected — it proves the bug exists).
The fixed version tests all **pass**.

## How to run

```bash
cd workspaces/T01_code_review_p3/workspace
python -m pytest tests/ -v
```
