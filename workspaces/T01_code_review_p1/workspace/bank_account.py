"""
bank_account.py — Buggy version with a classic TOCTOU race condition.

The race condition is in withdraw() and deposit():
    balance = get_balance()       # READ (T1)
    #  ⚡ Context switch here     # T2 modifies balance
    balance -= amount             # WRITE (T1) — overwrites T2's change
    commit(balance)               # COMMIT
"""

import time


# ── Shared "database" — simulates a remote key-value store ─────────

_BALANCE_DB: dict[int, float] = {}
_DB_LATENCY: float = 0.0       # simulated network delay (seconds)


def _db_read(key: int) -> float:
    """Read from the simulated database with optional latency."""
    if _DB_LATENCY:
        time.sleep(_DB_LATENCY)
    return _BALANCE_DB.get(key, 0.0)


def _db_write(key: int, value: float) -> None:
    """Write to the simulated database with optional latency."""
    if _DB_LATENCY:
        time.sleep(_DB_LATENCY)
    _BALANCE_DB[key] = value


class BankAccount:
    """
    A bank account with a deliberate race condition.

    The balance is stored in a simulated *external* data store (like
    a database or a remote API).  This is the most common real-world
    source of race conditions in banking code::

        current = db.get_balance(account_id)   # network call
        if current >= amount:
            new_balance = current - amount
            db.set_balance(account_id, new_balance)  # separate call

    The two network calls are *not* wrapped in a transaction, so
    concurrent requests can interleave.
    """

    def __init__(self, account_id: int, initial_balance: float = 0.0) -> None:
        self.account_id = account_id
        _BALANCE_DB[account_id] = initial_balance

    # ── Internal helpers (simulate remote DB round-trips) ────────────

    def get_balance(self) -> float:
        """Read balance from the simulated database."""
        return _db_read(self.account_id)

    def set_balance(self, new_balance: float) -> None:
        """Write balance to the simulated database."""
        _db_write(self.account_id, new_balance)

    # ── Public API (⚠️ RACE CONDITION HERE) ─────────────────────────

    def withdraw(self, amount: float) -> bool:
        """
        Withdraw money from the account.

        BUG: check-then-act across *two separate database calls* is
        not atomic.  Two concurrent callers can both pass the
        'sufficient funds' check before either subtraction commits,
        allowing an overdraft.
        """
        current = self.get_balance()          # DB READ → TOCTOU window
        if current < amount:
            return False                       # insufficient funds
        # ⚡⚡⚡ Thread switch happens here ⚡⚡⚡
        # The DB now has a different value but this thread still uses 'current'
        new_balance = current - amount
        self.set_balance(new_balance)          # DB WRITE — based on stale data
        return True

    def deposit(self, amount: float) -> None:
        """Deposit money (same TOCTOU bug — read‐modify‐write)."""
        current = self.get_balance()
        new_balance = current + amount
        self.set_balance(new_balance)

    def __repr__(self) -> str:
        return f"BankAccount(#{self.account_id}, balance={_db_read(self.account_id)})"
