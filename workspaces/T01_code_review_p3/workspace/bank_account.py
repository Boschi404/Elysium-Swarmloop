"""
bank_account.py — BUGGY VERSION (Race Condition)

This implementation has a classic TOCTOU (Time of Check, Time of Use) race condition.
Multiple threads can interleave reads and writes, causing lost updates.
"""

import time


class BankAccount:
    """Simple bank account with a deliberate race condition."""

    def __init__(self, owner: str, initial_balance: float = 0.0) -> None:
        self.owner = owner
        self.balance: float = initial_balance

    def deposit(self, amount: float) -> float:
        """Deposit money — NOT thread-safe."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        current = self.balance       # READ (TOCTOU window opens)
        time.sleep(0)                # yield GIL — guarantee thread switch
        new_balance = current + amount
        self.balance = new_balance   # WRITE (window closes)
        return self.balance

    def withdraw(self, amount: float) -> float:
        """Withdraw money — NOT thread-safe."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        current = self.balance       # READ
        time.sleep(0)                # yield GIL — force interleaving
        if current < amount:
            raise ValueError("Insufficient funds")
        new_balance = current - amount
        self.balance = new_balance   # WRITE
        return self.balance

    def get_balance(self) -> float:
        return self.balance

    def transfer_to(self, target: "BankAccount", amount: float) -> None:
        """Transfer between accounts — compound race condition."""
        self.withdraw(amount)        # TOCTOU window per call
        target.deposit(amount)

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"
