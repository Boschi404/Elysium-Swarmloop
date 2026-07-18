"""
buggy_bank.py — Banking account with a classic race condition.

BUG: The withdraw() and deposit() methods follow a read-modify-write pattern
that is NOT atomic. Between get_balance() and set_balance(), another thread
can mutate the balance, causing lost updates and corrupt state.

Example race:
  Thread A: balance = get_balance()    # reads 100
  Thread B: balance = get_balance()    # reads 100
  Thread A: balance -= 50 → set_balance(50)
  Thread B: balance -= 30 → set_balance(70)  # OVERSIGHT: should be 20!
  Final balance: 70  ✗  Correct: 20
"""

import threading
import time


class BuggyBankAccount:
    """A bank account with NO concurrency protection — vulnerable to race conditions."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self._balance = initial_balance

    def get_balance(self) -> float:
        """Return the current balance."""
        return self._balance

    def set_balance(self, amount: float) -> None:
        """Set the balance to the given amount."""
        # Artificially slow write to make the race condition easier to trigger.
        time.sleep(0.001)
        self._balance = amount

    def deposit(self, amount: float) -> None:
        """Deposit money: read → modify → write (non-atomic)."""
        if amount < 0:
            raise ValueError("Deposit amount must be non-negative")
        current = self.get_balance()
        new_balance = current + amount
        self.set_balance(new_balance)

    def withdraw(self, amount: float) -> bool:
        """Withdraw money: read → modify → write (non-atomic).

        Returns True if the withdrawal succeeded, False if insufficient funds.
        """
        if amount < 0:
            raise ValueError("Withdrawal amount must be non-negative")
        current = self.get_balance()
        if current < amount:
            return False
        new_balance = current - amount
        self.set_balance(new_balance)
        return True
