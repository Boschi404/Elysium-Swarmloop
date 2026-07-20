"""
bank_buggy.py — Banking account with a TOCTOU race condition.

The bug: withdraw() does a non-atomic read-modify-write:
    balance = get_balance()
    balance -= amount
    set_balance(balance)

Two threads executing simultaneously can both read the same old balance,
compute new values from it, and write back — the second write silently
overwrites the first, losing one of the updates.
"""

import threading


class UnsafeAccount:
    """A bank account whose withdraw() has a race condition."""

    def __init__(self, initial_balance: int = 0) -> None:
        self._balance = initial_balance

    # ── public helpers for the bug pattern ──────────────────────────────

    def get_balance(self) -> int:
        return self._balance

    def set_balance(self, new_balance: int) -> None:
        self._balance = new_balance

    # ── the bug ─────────────────────────────────────────────────────────

    def withdraw(self, amount: int) -> None:
        """BUGGY: 3-line read-modify-write that is NOT thread-safe."""
        balance = self.get_balance()
        balance -= amount
        self.set_balance(balance)

    # ── helper for tests ────────────────────────────────────────────────

    @property
    def balance(self) -> int:
        return self._balance
