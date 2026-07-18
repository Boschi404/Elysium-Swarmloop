"""
test_bank_race.py — Test that catches the race condition.

Strategy
────────
Launch N threads all doing concurrent withdrawals from the same account.
If the code is racy, the final balance will be **higher** than expected
(because some withdrawals are silently lost).  A fixed version always
produces the correct final balance.

Run with:  pytest -q tests/test_bank_race.py
"""

import threading

import pytest

# Import both the buggy and the fixed version
from bank_account import BankAccount
from bank_account_fixed import BankAccountFixed


# ── Helpers ──────────────────────────────────────────────────────────

def hammer_withdrawals(acc, thread_count: int, withdrawals_per_thread: int,
                       amount_per: int) -> None:
    """Launch *thread_count* threads, each doing *withdrawals_per_thread*
    withdrawals of *amount_per* from *acc*."""

    def worker() -> None:
        for _ in range(withdrawals_per_thread):
            acc.withdraw(amount_per)

    threads = [threading.Thread(target=worker) for _ in range(thread_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ── Tests ────────────────────────────────────────────────────────────

def test_buggy_version_demonstrates_race() -> None:
    """The buggy version MUST produce the wrong balance with 10 threads."""
    INITIAL = 100_000
    TOTAL_WITHDRAWAL = 99_999

    acc = BankAccount(initial_balance=INITIAL)
    hammer_withdrawals(acc, thread_count=10,
                       withdrawals_per_thread=1,
                       amount_per=TOTAL_WITHDRAWAL // 10)

    expected = INITIAL - TOTAL_WITHDRAWAL  # = 1
    # We assert the bug is PRESENT (balance is wrong).
    assert acc.get_balance() != expected, (
        f"BUG HIDDEN? Balance={acc.get_balance()}, expected={expected}. "
        "The race did not trigger — increase thread count or amount."
    )


def test_fixed_version_is_correct() -> None:
    """The fixed version MUST always produce the correct balance."""
    INITIAL = 100_000
    WITHDRAWAL_PER = 500
    THREADS = 10
    ITERS = 20

    acc = BankAccountFixed(initial_balance=INITIAL)
    hammer_withdrawals(acc, thread_count=THREADS,
                       withdrawals_per_thread=ITERS,
                       amount_per=WITHDRAWAL_PER)

    expected = INITIAL - (THREADS * ITERS * WITHDRAWAL_PER)
    assert acc.get_balance() == expected, (
        f"FIX FAILED: Balance={acc.get_balance()}, expected={expected}. "
        "Lock is not working correctly."
    )


def test_concurrent_deposit_and_withdraw() -> None:
    """Mixing deposits and withdrawals concurrently is also safe in
    the fixed version."""
    INITIAL = 10_000

    acc_fixed = BankAccountFixed(initial_balance=INITIAL)

    def depositor() -> None:
        for _ in range(50):
            acc_fixed.deposit(100)

    def withdrawer() -> None:
        for _ in range(50):
            acc_fixed.withdraw(100)

    threads = [
        threading.Thread(target=depositor),
        threading.Thread(target=withdrawer),
        threading.Thread(target=depositor),
        threading.Thread(target=withdrawer),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 4 threads × 50 ops × 100  = 20_000 net flow (2 deposits = +10_000,
    # 2 withdrawals = -10_000) → back to INITIAL
    assert acc_fixed.get_balance() == INITIAL, (
        f"Balance drifted: {acc_fixed.get_balance()}"
    )


def test_insufficient_funds_remains_correct_under_race() -> None:
    """Even in the fixed version, a withdrawal that would overdraw is
    correctly rejected — no lost money."""
    acc = BankAccountFixed(initial_balance=100)

    results = []
    lock = threading.Lock()

    def try_withdraw(amount: int) -> None:
        ok = acc.withdraw(amount)
        with lock:
            results.append(ok)

    # Two threads: one tries 80, the other tries 80.
    # Only ONE should succeed (since 80+80 > 100).
    threads = [
        threading.Thread(target=try_withdraw, args=(80,)),
        threading.Thread(target=try_withdraw, args=(80,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successes = sum(results)
    assert successes == 1, (
        f"Expected exactly 1 success, got {successes}. "
        "Insufficient-funds guard is broken."
    )
    assert acc.get_balance() == 20, (
        f"Expected balance=20, got {acc.get_balance()}"
    )
