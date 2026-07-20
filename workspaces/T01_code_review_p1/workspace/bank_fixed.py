"""
bank_fixed.py — Thread-safe banking account using a lock.

The fix wraps every read-modify-write inside a threading.Lock so that
only one thread can access the critical section at a time, guaranteeing
sequential consistency.

Alternative approaches (not shown, but equally valid):
  - threading.RLock (re-entrant, useful if withdraw calls another lock-guarded method)
  - An atomic compare-and-swap in languages that support it (e.g. Java AtomicInteger)
  - A dedicated database transaction with SERIALIZABLE isolation
"""

import threading


class SafeAccount:
    """A bank account whose withdraw() is serialised by a lock."""

    def __init__(self, initial_balance: int = 0) -> None:
        self._balance = initial_balance
        self._lock = threading.Lock()

    # ── helpers (NOT individually thread-safe; they rely on the caller
    #    holding _lock, or being called only from withdraw). ─────────────

    def get_balance(self) -> int:
        return self._balance

    def set_balance(self, new_balance: int) -> None:
        self._balance = new_balance

    # ── the fix ────────────────────────────────────────────────────────

    def withdraw(self, amount: int) -> None:
        """Thread-safe: the entire read-modify-write is atomic."""
        with self._lock:
            balance = self.get_balance()
            balance -= amount
            self.set_balance(balance)

    # ── convenience ─────────────────────────────────────────────────────

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        with self._lock:
            balance = self.get_balance()
            balance += amount
            self.set_balance(balance)
