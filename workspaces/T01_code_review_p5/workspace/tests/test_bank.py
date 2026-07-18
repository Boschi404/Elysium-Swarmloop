"""Tests for the race condition bug — run with: pytest tests/ from workspace."""
import sys
import os
import threading

# Ensure the workspace root is on sys.path so imports work
_this_dir = os.path.dirname(os.path.abspath(__file__))
_workspace = os.path.dirname(_this_dir)
if _workspace not in sys.path:
    sys.path.insert(0, _workspace)

from buggy_bank import BuggyBankAccount
from fixed_bank import LockedBankAccount

import pytest

NUM_THREADS = 10
WITHDRAW_AMOUNT = 10
INITIAL_BALANCE = 100


# ============================================================
# Unit tests — single-threaded correctness
# ============================================================

class TestBuggyBankSingleThread:
    """Single-threaded: even the buggy bank passes these."""

    def test_initial_balance(self):
        acct = BuggyBankAccount(100)
        assert acct.get_balance() == 100

    def test_deposit(self):
        acct = BuggyBankAccount(50)
        acct.deposit(25)
        assert acct.get_balance() == 75

    def test_withdraw(self):
        acct = BuggyBankAccount(50)
        ok = acct.withdraw(20)
        assert ok is True
        assert acct.get_balance() == 30

    def test_insufficient_funds(self):
        acct = BuggyBankAccount(10)
        ok = acct.withdraw(100)
        assert ok is False
        assert acct.get_balance() == 10

    def test_negative_deposit_raises(self):
        acct = BuggyBankAccount(50)
        with pytest.raises(ValueError):
            acct.deposit(-5)

    def test_negative_withdraw_raises(self):
        acct = BuggyBankAccount(50)
        with pytest.raises(ValueError):
            acct.withdraw(-5)


# ============================================================
# Race-condition test — catches the bug
# ============================================================

class TestRaceCondition:

    def _run_concurrent_withdrawals(self, account_class):
        account = account_class(INITIAL_BALANCE)

        def worker():
            account.withdraw(WITHDRAW_AMOUNT)

        threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return account.get_balance()

    def test_buggy_bank_has_race_condition(self):
        """The buggy bank will have a non-zero balance (lost updates)."""
        balance = self._run_concurrent_withdrawals(BuggyBankAccount)
        assert balance != 0, (
            f"Expected race condition to corrupt balance, but got {balance}. "
            f"The artificial sleep may not be enough on this platform."
        )

    def test_locked_bank_prevents_race(self):
        """The locked bank always has the correct final balance (0)."""
        balance = self._run_concurrent_withdrawals(LockedBankAccount)
        assert balance == 0, (
            f"Locked bank should have balance 0 after "
            f"{NUM_THREADS}×{WITHDRAW_AMOUNT} withdrawals from {INITIAL_BALANCE}, "
            f"but got {balance}."
        )


# ============================================================
# Deterministic race-proving test (no timing dependency)
# ============================================================

class TestDeterministicRace:

    def test_deterministic_interleaving(self):
        """Force both threads to read the stale balance before either writes.

        Correct:  100 - 30 - 50 = 20
        With race: both read 100, last write wins → 50 or 70
        """
        import time
        barrier = threading.Barrier(2)
        account = BuggyBankAccount(100)

        def worker_a():
            bal = account.get_balance()     # reads 100
            barrier.wait()                   # sync — B also reads 100 now
            time.sleep(0.02)                 # ensure B has read before we write
            account.set_balance(bal - 30)    # writes 70 (but B is about to overwrite)

        def worker_b():
            bal = account.get_balance()     # ALSO reads 100 (stale!)
            barrier.wait()
            time.sleep(0.01)
            account.set_balance(bal - 50)    # writes 50 — LOST A's update!

        t1 = threading.Thread(target=worker_a)
        t2 = threading.Thread(target=worker_b)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        final = account.get_balance()
        # Correct would be 20; due to the race it'll be 50 or 70 (≠ 20)
        assert final != 20, (
            f"Race should have produced wrong balance, got {final}"
        )


# ============================================================
# Stress test for the fixed version
# ============================================================

class TestFixedBankStress:

    def test_balanced_ops(self):
        """50 threads, balanced deposits + withdrawals → final == initial."""
        account = LockedBankAccount(500)
        n_threads = 50

        def worker_deposit():
            for _ in range(20):
                account.deposit(10)

        def worker_withdraw():
            for _ in range(20):
                account.withdraw(10)

        threads = []
        for i in range(n_threads):
            t = threading.Thread(target=worker_deposit if i % 2 == 0 else worker_withdraw)
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert account.get_balance() == 500, (
            f"Expected 500 after balanced ops, got {account.get_balance()}"
        )

    def test_high_volume_deposits(self):
        """Many concurrent deposits: all must sum correctly."""
        account = LockedBankAccount(0)
        n_threads = 20
        per_thread = 100

        def worker():
            for _ in range(per_thread):
                account.deposit(5)

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = n_threads * per_thread * 5
        assert account.get_balance() == expected, (
            f"Expected {expected}, got {account.get_balance()}"
        )
