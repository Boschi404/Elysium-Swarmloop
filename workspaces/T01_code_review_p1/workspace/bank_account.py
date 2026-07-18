"""
bank_account.py — Banking account with a deliberate race condition.

BUG: The withdraw() method performs a read-modify-write (get_balance →
subtract → set_balance) as three separate operations. When two threads
execute concurrently, their reads interleave and one update is silently lost,
letting the account go overdrawn below zero.

FIXED VERSION: See bank_account_fixed.py
"""

import threading
import time


class BankAccount:
    """A simple bank account with a classic TOCTOU race condition."""

    def __init__(self, initial_balance: int = 0):
        self._balance = initial_balance

    # ── Buggy read/write pair (no lock) ──────────────────────────────

    def get_balance(self) -> int:
        """Return the current balance (non-atomic read)."""
        return self._balance

    def set_balance(self, amount: int) -> None:
        """Overwrite the balance (non-atomic write).

        A tiny sleep amplifies the race window during testing so the
        interleaving is reproducible without a massive number of threads.
        """
        time.sleep(0.000_010)          # <-- widens the race window
        self._balance = amount

    # ── The problematic method ───────────────────────────────────────

    def withdraw(self, amount: int) -> bool:
        """Withdraw *amount* from the account.

        BUG: This is a classic **check-then-act** race.
        Thread interleaving that causes the bug:

            Thread A                        Thread B
            ─────────                       ─────────
            balance = get_balance()  → 100
                                            balance = get_balance()  → 100
            balance -= 20            → 80
                                            balance -= 50            → 50
            set_balance(80)
                                            set_balance(50)    ← OVERSIGHT!

        Both threads read 100. A withdraws 20 (→ 80), B withdraws 50 (→ 50).
        Because B's write *overwrites* A's, the final balance is 50 instead
        of 30.  Worse, if amount exceeds the *stale* balance, the guard
        below can pass for both threads, allowing the account to go
        negative.
        """
        current = self.get_balance()
        if current < amount:
            return False                 # insufficient funds
        new_balance = current - amount
        time.sleep(0.000_010)            # <-- widens the race window
        self.set_balance(new_balance)
        return True

    def deposit(self, amount: int) -> None:
        """Deposit *amount* (also racy, though less dangerous)."""
        current = self.get_balance()
        self.set_balance(current + amount)


def bug_demo() -> None:
    """Demonstrate the race condition with two concurrent withdrawals.

    Expected outcome:  balance = 100 - 20 - 50 = 30
    Actual outcome:    balance = 50  (B's write clobbers A's)
    """
    acc = BankAccount(initial_balance=100)

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
    print(f"BUG PRESENT: {acc.get_balance() != 30}")


if __name__ == "__main__":
    bug_demo()
