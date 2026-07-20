"""
test_bank_account.py — Tests that detect and verify race conditions.

Uses threading + barriers to ensure concurrent operations overlap, making
the race condition reproducible within a short test window.
"""

import sys
import os
import threading
from typing import List

# Ensure the workspace is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bank_account import BankAccount          # buggy version
from bank_account_fixed import BankAccountFixed  # fixed version

import pytest

# ---------------------------------------------------------------------------
# Helper — run many concurrent withdrawals
# ---------------------------------------------------------------------------

CONCURRENCY = 50      # number of racing threads
INITIAL = 5000.0
WITHDRAW = 100.0


def _race_deposits(account, amount, barrier, results, errors, n=CONCURRENCY):
    """Target for threads: race *n* deposits simultaneously."""
    barrier.wait()
    try:
        account.deposit(amount)
        results.append(True)
    except Exception as e:
        errors.append(e)


def _race_withdrawals(account, amount, barrier, results, errors):
    """Target for threads: race withdrawals."""
    barrier.wait()
    try:
        account.withdraw(amount)
        results.append(amount)
    except Exception as e:
        errors.append(e)


# ---------------------------------------------------------------------------
# 1.  Catch the race condition in the buggy version
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason="Demonstrates the TOCTOU race condition — expected to fail")
def test_race_condition_deposit_detected():
    """Prove the buggy version loses updates under concurrent deposits."""
    account = BankAccount("TEST", 0.0)
    amount = 10.0
    N = CONCURRENCY
    barrier = threading.Barrier(N)
    results: List[bool] = []
    errors: List[Exception] = []

    threads = [
        threading.Thread(
            target=_race_deposits, args=(account, amount, barrier, results, errors, N)
        )
        for _ in range(N)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_balance = N * amount
    actual_balance = account.get_balance()

    # Under the race condition the balance is almost always < expected.
    # We assert the *exact* expected balance — the buggy version will fail.
    assert actual_balance == expected_balance, (
        f"RACE CONDITION DETECTED: expected {expected_balance:.0f}, "
        f"got {actual_balance:.0f} — {expected_balance - actual_balance:.0f} units lost"
    )


@pytest.mark.xfail(strict=True, reason="Demonstrates the TOCTOU race condition — expected to fail")
def test_race_condition_withdraw_detected():
    """Prove the buggy version loses updates under concurrent withdrawals."""
    account = BankAccount("TEST", INITIAL)
    barrier = threading.Barrier(CONCURRENCY)
    results: List[float] = []
    errors: List[Exception] = []

    threads = [
        threading.Thread(
            target=_race_withdrawals,
            args=(account, WITHDRAW, barrier, results, errors),
        )
        for _ in range(CONCURRENCY)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_balance = INITIAL - CONCURRENCY * WITHDRAW
    actual_balance = account.get_balance()

    # The buggy version will likely have a wrong balance (lost updates).
    assert actual_balance == expected_balance, (
        f"RACE CONDITION DETECTED: expected {expected_balance:.0f}, "
        f"got {actual_balance:.0f} — "
        f"{actual_balance - expected_balance:.0f} units left (withdrawals lost)"
    )


# ---------------------------------------------------------------------------
# 2.  Verify the fixed version passes under the same concurrent load
# ---------------------------------------------------------------------------


def test_fixed_version_no_race_deposits():
    """The locked version should produce the correct final balance."""
    account = BankAccountFixed("TEST", 0.0)
    amount = 10.0
    N = CONCURRENCY
    barrier = threading.Barrier(N)
    results: List[bool] = []
    errors: List[Exception] = []

    threads = [
        threading.Thread(
            target=_race_deposits, args=(account, amount, barrier, results, errors, N)
        )
        for _ in range(N)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = N * amount
    actual = account.get_balance()
    assert actual == expected, f"Locked version: expected {expected}, got {actual}"


def test_fixed_version_no_race_withdrawals():
    """The locked version should maintain consistent balance under concurrent withdrawals."""
    account = BankAccountFixed("TEST", INITIAL)
    barrier = threading.Barrier(CONCURRENCY)
    results: List[float] = []
    errors: List[Exception] = []

    threads = [
        threading.Thread(
            target=_race_withdrawals,
            args=(account, WITHDRAW, barrier, results, errors),
        )
        for _ in range(CONCURRENCY)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = INITIAL - CONCURRENCY * WITHDRAW
    actual = account.get_balance()
    assert actual == expected, f"Locked version: expected {expected}, got {actual}"


def test_fixed_version_negative_balance_prevented():
    """With proper locking, the invariant (balance >= 0 after operations)
    must hold.  With the race condition, two concurrent withdrawals can
    both pass the check and then both apply."""
    account = BankAccountFixed("TEST", 50.0)
    barrier = threading.Barrier(3)
    results: List[float] = []
    errors: List[Exception] = []

    threads = [
        threading.Thread(
            target=_race_withdrawals,
            args=(account, 40.0, barrier, results, errors),
        )
        for _ in range(3)  # 3 × 40 = 120 > 50
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # With the race, *all three* might succeed, leaving -70.
    # With proper locking, at most 1 succeeds and the rest raise.
    final = account.get_balance()
    successes = len([r for r in results if r is not False])  # True = amount
    assert 0 <= final <= 50.0, (
        f"Race caused negative balance! final={final}, "
        f"successful withdrawals={successes}"
    )


# ---------------------------------------------------------------------------
# 3.  Bonus: concurrent deposits + withdrawals (mixed workload)
# ---------------------------------------------------------------------------


def test_mixed_concurrent_workload():
    """Verifies the lock works correctly when deposits and withdrawals
    interleave."""
    account = BankAccountFixed("TEST", 1000.0)
    n_deposits = 30
    n_withdrawals = 20
    barrier = threading.Barrier(n_deposits + n_withdrawals)
    results: List[bool] = []
    errors: List[Exception] = []

    def deposit_worker():
        barrier.wait()
        account.deposit(50.0)
        results.append(True)

    def withdraw_worker():
        barrier.wait()
        account.withdraw(30.0)
        results.append(True)

    threads = [threading.Thread(target=deposit_worker) for _ in range(n_deposits)]
    threads += [threading.Thread(target=withdraw_worker) for _ in range(n_withdrawals)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = 1000.0 + n_deposits * 50.0 - n_withdrawals * 30.0
    actual = account.get_balance()
    assert actual == expected, f"Mixed workload: expected {expected}, got {actual}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
