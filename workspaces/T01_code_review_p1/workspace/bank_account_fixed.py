"""
bank_account_fixed.py — FIXED VERSION using threading.Lock.

Eliminates the race condition by serialising concurrent access with
a reentrant lock.  Alternative approaches include:

  - threading.Lock  (simplest Python-level fix, used here)
  - threading.RLock (if methods call each other recursively)
  - queue.Queue     (producer-consumer pattern)
  - atomic DB transaction (e.g. `UPDATE ... SET balance = balance - ?`)
"""

import threading


class BankAccountFixed:
    """Thread-safe bank account protected by a reentrant lock."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance
        self._lock = threading.Lock()

    def get_balance(self) -> float:
        """Return the current balance (thread-safe read)."""
        with self._lock:
            return self._balance

    def set_balance(self, balance: float) -> None:
        """Set the balance (thread-safe write)."""
        with self._lock:
            self._balance = balance

    def withdraw(self, amount: float) -> bool:
        """
        Withdraw *amount* atomically.

        The entire read-modify-write is protected by the lock,
        so no other thread can interleave.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with self._lock:                        # ← CRITICAL SECTION
            if self._balance < amount:
                return False
            self._balance -= amount             # atomic read-modify-write
        return True

    def deposit(self, amount: float) -> None:
        """Deposit *amount* atomically."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        with self._lock:
            self._balance += amount

    # ── Alternative: atomic DB-style operation ──────────────────
    def transfer_to(self, other: "BankAccountFixed", amount: float) -> bool:
        """
        Transfer *amount* to another account (two-phase atomic).

        Deadlock-avoidance: always lock in consistent order (by id).
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Lock in address order to prevent deadlock
        first, second = sorted((id(self), id(other)))
        locks = {id(self): self._lock, id(other): other._lock}

        with locks[first]:
            with locks[second]:
                if self._balance < amount:
                    return False
                self._balance -= amount
                other._balance += amount
        return True
