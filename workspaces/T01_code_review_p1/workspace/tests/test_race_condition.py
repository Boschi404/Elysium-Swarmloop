"""
tests/test_race_condition.py

Demonstrates the race condition in bank_account.py and verifies the
fixed version in bank_account_fixed.py.

Uses threading.Barrier to synchronise thread start — all threads hit
the withdraw() call within a few microseconds of each other,
maximising the chance of interleaving.
"""

import threading
import sys
import os

# Ensure workspace is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bank_account import BankAccount
from bank_account_fixed import BankAccountFixed

NUM_THREADS = 10
WITHDRAW_AMOUNT = 10
INITIAL_BALANCE = 100  # NUM_THREADS * WITHDRAW_AMOUNT


# ── Test: buggy version loses updates ──────────────────────────

def test_buggy_account_exposes_race_condition():
    """
    The buggy BankAccount.withdraw() has a non-atomic read-modify-write.

    With N concurrent threads each withdrawing €10 from €100,
    the final balance is almost never €0 because overlapping reads
    cause lost updates.
    """
    account = BankAccount(INITIAL_BALANCE)
    errors = []
    barrier = threading.Barrier(NUM_THREADS)  # synchronised start

    def withdraw():
        barrier.wait()  # all threads hit withdraw() at nearly the same time
        try:
            account.withdraw(WITHDRAW_AMOUNT)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=withdraw) for _ in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The buggy balance is typically €30–€70 (not €0).
    # We assert it's NOT the correct expected value to EXPOSE the bug.
    # (This test will PASS when the bug is present, FAIL if fixed —
    #  that's intentional: it documents that the bug exists.)
    final = account.get_balance()
    expected = INITIAL_BALANCE - NUM_THREADS * WITHDRAW_AMOUNT  # €0

    print(f"\n[BUGGY] Initial={INITIAL_BALANCE}, "
          f"Withdrew={NUM_THREADS}×{WITHDRAW_AMOUNT}, "
          f"Expected={expected}, Got={final}")

    # With the race condition, final balance is > expected (lost updates)
    assert final != expected, (
        f"BUG NOT REPRODUCED — balance is {final} instead of expected {expected}. "
        f"The race condition did not manifest. Try increasing NUM_THREADS "
        f"or running on a multi-core machine."
    )


# ── Test: fixed version is race-free ───────────────────────────

def test_fixed_account_no_race_condition():
    """
    BankAccountFixed uses threading.Lock to protect the critical section.

    With N concurrent threads each withdrawing €10 from €100,
    the final balance is ALWAYS exactly €0.
    """
    account = BankAccountFixed(INITIAL_BALANCE)
    errors = []
    barrier = threading.Barrier(NUM_THREADS)

    def withdraw():
        barrier.wait()
        try:
            account.withdraw(WITHDRAW_AMOUNT)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=withdraw) for _ in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = account.get_balance()
    expected = INITIAL_BALANCE - NUM_THREADS * WITHDRAW_AMOUNT  # €0

    print(f"\n[FIXED] Initial={INITIAL_BALANCE}, "
          f"Withdrew={NUM_THREADS}×{WITHDRAW_AMOUNT}, "
          f"Expected={expected}, Got={final}")

    assert final == expected, (
        f"Race condition still present! Expected {expected}, got {final}. "
        f"Lock may not be protecting the critical section."
    )
    assert not errors, f"Thread errors: {errors}"


# ── Test: edge cases ───────────────────────────────────────────

def test_withdraw_negative_amount():
    """Both versions should reject negative/zero amounts."""
    for account in (BankAccount(100), BankAccountFixed(100)):
        try:
            account.withdraw(-10)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        try:
            account.withdraw(0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


def test_insufficient_funds():
    """Withdrawing more than balance should return False."""
    for account_cls in (BankAccount, BankAccountFixed):
        account = account_cls(50)
        result = account.withdraw(100)
        assert result is False, "Should return False for insufficient funds"
        assert account.get_balance() == 50, "Balance should not change"


def test_high_contention():
    """
    Stress test: 100 threads, each withdrawing €1 from €100.

    The buggy version should lose ~€50 (the exact amount is
    non-deterministic but almost never €0).
    """
    account = BankAccount(100)
    n = 100
    errors = []
    barrier = threading.Barrier(n)

    def withdraw():
        barrier.wait()
        try:
            account.withdraw(1)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=withdraw) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = account.get_balance()
    print(f"\n[HIGH CONTENTION] 100×€1 from €100 → final={final}")
    # Almost certainly not 0 — we expect ~€20–€70 lost
    assert final > 0, (
        f"BUG NOT REPRODUCED under high contention — balance is {final}. "
        f"This is very unusual — race may not reproduce on this platform."
    )


# ── Test: fixed version survives high contention ───────────────

def test_fixed_high_contention():
    """100 threads withdrawing €1 from €100 → final must be exactly €0."""
    account = BankAccountFixed(100)
    n = 100
    errors = []
    barrier = threading.Barrier(n)

    def withdraw():
        barrier.wait()
        try:
            account.withdraw(1)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=withdraw) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = account.get_balance()
    print(f"\n[FIXED HIGH CONTENTION] 100×€1 from €100 → final={final}")
    assert final == 0, f"Locked version should have €0, got {final}"
    assert not errors, f"Thread errors: {errors}"
