"""
fixed_bank.py — Banking account with race conditions fixed via threading.Lock.

FIX: Wrap every read-modify-write sequence in a mutex (threading.Lock).
This guarantees that only ONE thread at a time can observe and mutate the
balance, eliminating the lost-update problem.

Additional improvements:
  - Lock acquisition via context manager (with self._lock:) — exception-safe.
  - All internal state access happens inside the lock — no need for separate
    get_balance/set_balance helpers; the lock protects the critical section.
  - Atomic compound operations: read, check, write all happen under one lock
    acquisition, so no other thread can interleave.
"""

import threading
import time


class LockedBankAccount:
    """A bank account protected by threading.Lock — race-condition-free."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance
        self._lock = threading.Lock()

    def get_balance(self) -> float:
        """Return the current balance (thread-safe read)."""
        with self._lock:
            return self._balance

    def set_balance(self, amount: float) -> None:
        """Set the balance (thread-safe write)."""
        # Still keep the artificial delay so we can verify the fix holds.
        with self._lock:
            time.sleep(0.001)
            self._balance = amount

    def deposit(self, amount: float) -> None:
        """Thread-safe deposit — whole critical section under a single lock."""
        if amount < 0:
            raise ValueError("Deposit amount must be non-negative")
        with self._lock:
            new_balance = self._balance + amount
            time.sleep(0.001)
            self._balance = new_balance

    def withdraw(self, amount: float) -> bool:
        """Thread-safe withdrawal — read, check, and write happen atomically."""
        if amount < 0:
            raise ValueError("Withdrawal amount must be non-negative")
        with self._lock:
            if self._balance < amount:
                return False
            new_balance = self._balance - amount
            time.sleep(0.001)
            self._balance = new_balance
            return True


# ---- Alternative: RLock-based for re-entrant safety ----

class ReentrantBankAccount:
    """Same fix using threading.RLock — useful when public methods call each other."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance
        self._lock = threading.RLock()

    def get_balance(self) -> float:
        with self._lock:
            return self._balance

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be non-negative")
        with self._lock:
            self._balance += amount

    def withdraw(self, amount: float) -> bool:
        if amount < 0:
            raise ValueError("Withdrawal amount must be non-negative")
        with self._lock:
            if self._balance < amount:
                return False
            self._balance -= amount
            return True


# ---- Alternative: threading.atomic via a higher-level primitive ----

class AtomicBankAccount:
    """Uses a lock internally but exposes a compare-and-swap style interface.

    This mirrors how databases handle atomic updates: the operation is a
    single, indivisible unit.
    """

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance
        self._lock = threading.Lock()

    def apply(self, func):
        """Apply a pure function to the balance atomically.

        The function receives the current balance and returns the new balance.
        """
        with self._lock:
            self._balance = func(self._balance)
            return self._balance

    def get_balance(self) -> float:
        with self._lock:
            return self._balance

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be non-negative")
        self.apply(lambda b: b + amount)

    def withdraw(self, amount: float) -> bool:
        if amount < 0:
            raise ValueError("Withdrawal amount must be non-negative")
        success = False

        def _withdraw(b):
            nonlocal success
            if b < amount:
                success = False
                return b
            success = True
            return b - amount

        self.apply(_withdraw)
        return success
