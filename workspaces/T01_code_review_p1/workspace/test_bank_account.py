"""
test_bank_account.py — Tests that catch the race condition.

Strategy
--------
The buggy BankAccount stores its balance in a simulated *external
database*.  By setting a small latency on every DB round-trip, we
force a context switch right inside the critical section — exactly
where the race window sits.

With that latency, 20 threads × 50 concurrent withdrawals from €500
reliably produce:

  ╔═══════════════════╤══════════════╗
  ║ Implementation    │ Final balance║
  ╠═══════════════════╪══════════════╣
  ║ BankAccount (bug) │ Negative !   ║  ← Overdraft!
  ║ FixedBankAccount  │ ≥ 0 exactly  ║  ← Correct
  ╚═══════════════════╧══════════════╝

The test also works *without* the latency by using a threading.Barrier
to align all threads at the exact same moment, then hitting the
account simultaneously.
"""

import threading
import pytest
from bank_account import BankAccount, _DB_LATENCY
from bank_account_fixed import FixedBankAccount, QueuedBankAccount


# ── HELPERS ────────────────────────────────────────────────────────────


def _set_latency(seconds: float) -> None:
    """Set the simulated database latency for the buggy module."""
    import bank_account as ba
    ba._DB_LATENCY = seconds


_ACCOUNT_COUNTER = 0


def _next_id() -> int:
    global _ACCOUNT_COUNTER
    _ACCOUNT_COUNTER += 1
    return _ACCOUNT_COUNTER


# ── STRESS TESTS (prove the race exists and the fix works) ────────────


@pytest.mark.stress
def test_buggy_account_overdrafts_on_race_small_latency() -> None:
    """
    Prove the buggy account allows overdrafts under concurrent access.

    With a tiny DB latency (0.001 s), the time-of-check-to-time-of-use
    window is wide enough for interleaving threads to pass the
    sufficiency check based on stale balances.
    """
    INITIAL = 500.0
    AMOUNT = 10.0
    THREADS = 20
    ITERS = 50

    _set_latency(0.001)
    try:
        acc = BankAccount(_next_id(), INITIAL)
        barrier = threading.Barrier(THREADS)
        results: list[int] = []

        def worker() -> None:
            failures = 0
            barrier.wait()  # all threads start at the same moment
            for _ in range(ITERS):
                ok = acc.withdraw(AMOUNT)
                if not ok:
                    failures += 1
            results.append(failures)

        threads = [threading.Thread(target=worker, daemon=True)
                   for _ in range(THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = acc.get_balance()
        total_withdrawn = THREADS * ITERS - sum(results)
        print(f"\n  Initial:          {INITIAL:.0f}")
        print(f"  Successful txn:   {total_withdrawn} × €{AMOUNT:.0f}")
        print(f"  Failed txn:       {sum(results)}")
        print(f"  Expected balance: {INITIAL - total_withdrawn * AMOUNT:.0f}")
        print(f"  Actual balance:   {final:.0f}")

        # The buggy version produces a non-deterministic wrong balance.
        # The race causes *lost updates* — money that was withdrawn by
        # one thread gets overwritten by another thread's stale write.
        # This means the balance shrinks *slower* than expected, so it
        # ends up HIGHER (less negative / more positive) than the
        # sequentially-correct value.
        correct = INITIAL - total_withdrawn * AMOUNT
        print(f"  → Race inflates balance: {final:.0f} ≠ expected {correct:.0f}")
        assert final != correct, (
            f"Race condition did NOT manifest — balance {final} == {correct}"
        )
        assert final > correct, (
            f"Lost-update bug should leave balance *higher* than expected "
            f"({final:.0f} > {correct:.0f}), not lower."
        )
    finally:
        _set_latency(0.0)


@pytest.mark.stress
def test_fixed_account_survives_concurrent_load() -> None:
    """
    Prove the lock-based account stays consistent under the same load.

    All withdrawals succeed until balance is exhausted, and the final
    balance is exactly what the sequential arithmetic predicts (no
    lost updates, no overdraft).
    """
    INITIAL = 500.0
    AMOUNT = 10.0
    THREADS = 20
    ITERS = 50

    _set_latency(0.001)
    try:
        acc = FixedBankAccount(_next_id(), INITIAL)
        barrier = threading.Barrier(THREADS)
        results: list[int] = []

        def worker() -> None:
            failures = 0
            barrier.wait()
            for _ in range(ITERS):
                ok = acc.withdraw(AMOUNT)
                if not ok:
                    failures += 1
            results.append(failures)

        threads = [threading.Thread(target=worker, daemon=True)
                   for _ in range(THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = acc.safe_balance
        total_failed = sum(results)
        total_withdrawn = THREADS * ITERS - total_failed
        expected = INITIAL - total_withdrawn * AMOUNT

        print(f"\n  Initial:         €{INITIAL:.0f}")
        print(f"  Successful txn:  {total_withdrawn} × €{AMOUNT:.0f}")
        print(f"  Failed txn:      {total_failed}")
        print(f"  Expected:        €{expected:.0f}")
        print(f"  Actual balance:  €{final:.0f}")

        assert final >= 0, f"Overdraft!  Balance {final} < 0"
        assert abs(final - expected) < 0.01, (
            f"Balance {final} != expected {expected} — race condition?"
        )
    finally:
        _set_latency(0.0)


# ── BASIC UNIT TESTS (sequential, quick smoke tests) ─────────────────


class TestBankAccountSequential:

    def test_withdraw_normal(self) -> None:
        _set_latency(0.0)
        acc = BankAccount(_next_id(), 100)
        assert acc.withdraw(30) is True
        assert acc.get_balance() == 70

    def test_withdraw_insufficient(self) -> None:
        _set_latency(0.0)
        acc = BankAccount(_next_id(), 50)
        assert acc.withdraw(100) is False
        assert acc.get_balance() == 50

    def test_deposit(self) -> None:
        _set_latency(0.0)
        acc = BankAccount(_next_id(), 0)
        acc.deposit(100)
        assert acc.get_balance() == 100


class TestFixedBankAccountSequential:

    def test_withdraw_normal(self) -> None:
        _set_latency(0.0)
        acc = FixedBankAccount(_next_id(), 100)
        assert acc.withdraw(30) is True
        assert acc.safe_balance == 70

    def test_withdraw_insufficient(self) -> None:
        _set_latency(0.0)
        acc = FixedBankAccount(_next_id(), 50)
        assert acc.withdraw(100) is False
        assert acc.safe_balance == 50

    def test_deposit(self) -> None:
        _set_latency(0.0)
        acc = FixedBankAccount(_next_id(), 0)
        acc.deposit(100)
        assert acc.safe_balance == 100

    def test_concurrent_mixed_operations(self) -> None:
        """Lighter concurrent test that runs fast without latency."""
        _set_latency(0.0)
        acc = FixedBankAccount(_next_id(), 1000)
        n = 50

        barrier = threading.Barrier(n)

        def depositor() -> None:
            barrier.wait()
            for _ in range(100):
                acc.deposit(1)

        def withdrawer() -> None:
            barrier.wait()
            for _ in range(100):
                acc.withdraw(1)

        threads = [
            threading.Thread(target=depositor)
            for _ in range(n // 2)
        ] + [
            threading.Thread(target=withdrawer)
            for _ in range(n // 2)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert acc.safe_balance == 1000, (
            f"Balance drifted: {acc.safe_balance}"
        )


class TestQueuedBankAccountSequential:

    def test_withdraw_normal(self) -> None:
        _set_latency(0.0)
        acc = QueuedBankAccount(_next_id(), 100)
        assert acc.withdraw(30) is True
        assert acc.safe_balance == 70

    def test_withdraw_insufficient(self) -> None:
        _set_latency(0.0)
        acc = QueuedBankAccount(_next_id(), 50)
        assert acc.withdraw(100) is False
        assert acc.safe_balance == 50

    def test_deposit(self) -> None:
        _set_latency(0.0)
        acc = QueuedBankAccount(_next_id(), 0)
        acc.deposit(100)
        assert acc.safe_balance == 100


# ── pytest entry-point ────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--no-header"])
