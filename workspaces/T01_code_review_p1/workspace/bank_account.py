"""
bank_account.py — BUGGY VERSION with race condition.

The classic TOCTOU (Time-of-check to Time-of-use) race condition:
    balance = get_balance()   # READ
    balance -= amount         # MODIFY (local)
    set_balance(balance)      # WRITE

Two concurrent threads can interleave here, producing lost updates.

Under CPython the GIL protects individual bytecode instructions,
so a simple attribute write (self._balance = x) appears atomic.
We add a tiny sleep to simulate the real-world scenario where a
DB query, API call, or file I/O sits between the read and write,
allowing the thread switch that triggers the race.
"""

import time


class BankAccount:
    """A bank account with a classic read-modify-write race condition."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance

    def get_balance(self) -> float:
        """Return the current balance."""
        return self._balance

    def set_balance(self, balance: float) -> None:
        """Set the balance (simulates a DB/API write)."""
        self._balance = balance

    # ── Bug: this method is NOT thread-safe ──────────────────────
    def withdraw(self, amount: float) -> bool:
        """
        Withdraw *amount* from the account.

        BUG: read-modify-write is not atomic.
        Thread A reads balance = 100
        Thread B reads balance = 100
        Thread A writes balance = 100 - 50 = 50
        Thread B writes balance = 100 - 30 = 70   ← 30€ LOST!
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        current = self.get_balance()    # READ
        time.sleep(0.0001)              # ← force GIL switch (simulates DB/API latency)
        if current < amount:
            return False                # Insufficient funds

        new_balance = current - amount  # MODIFY
        time.sleep(0.0001)              # ← force GIL switch
        self.set_balance(new_balance)   # WRITE
        return True

    def deposit(self, amount: float) -> None:
        """Deposit *amount* (also has the same race condition)."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        current = self.get_balance()
        time.sleep(0.0001)
        self.set_balance(current + amount)
