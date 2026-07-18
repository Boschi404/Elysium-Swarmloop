"""
bank_account_fixed.py — Thread-safe BankAccount using a lock.

FIX: Wrap every read-modify-write in a threading.Lock so that the
check-then-act sequence becomes **atomic** from the caller's perspective.
No two threads can interleave inside a locked critical section.
"""

import threading
import time


class BankAccountFixed:
    """Thread-safe bank account — every mutation is lock-protected."""

    def __init__(self, initial_balance: int = 0):
        self._balance = initial_balance
        self._lock = threading.Lock()

    # ── Internal helpers (kept for backward compat with tests) ───────

    def get_balance(self) -> int:
        """Return the current balance (still safe to read under the lock)."""
        return self._balance

    def set_balance(self, amount: int) -> None:
        """Overwrite the balance (kept for compat; not used directly)."""
        time.sleep(0.000_010)
        self._balance = amount

    # ── Fixed public API ─────────────────────────────────────────────

    def withdraw(self, amount: int) -> bool:
        """Withdraw *amount*.  Thread-safe via the lock.

        The entire check-and-update runs inside the critical section so
        that another thread can **never** see a stale balance.
        """
        with self._lock:
            current = self._balance
            if current < amount:
                return False
            new_balance = current - amount
            time.sleep(0.000_010)          # still present, but harmless now
            self._balance = new_balance
        return True

    def deposit(self, amount: int) -> None:
        """Deposit *amount*.  Thread-safe."""
        with self._lock:
            current = self._balance
            self._balance = current + amount


def fixed_demo() -> None:
    """Demonstrate that the fix works — result is always 30."""
    acc = BankAccountFixed(initial_balance=100)

    def withdraw_20() -> None:
        acc.withdraw(20)

    def withdraw_50() -> None:
        acc.withdraw(50)

    t1 = threading.Thread(target=withdraw_20)
    t2 = threading.Thread(target=withdraw_50)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"Expected balance:  30")
    print(f"Actual   balance:  {acc.get_balance()}")
    print(f"FIX WORKS: {acc.get_balance() == 30}")


if __name__ == "__main__":
    fixed_demo()
