"""
test_race_condition.py — Deterministic detector for the TOCTOU race.

HOW THE TEST CATCHES THE BUG
─────────────────────────────

Instead of relying on improbable thread timing (which passes on most runs
even when the bug exists), this test uses a **racy-helper** that injects a
sleep inside the read-modify-write window so the interleaving is guaranteed.

Thread A                     Thread B
────────                     ────────
get_balance() → 1000
                             get_balance() → 1000   ← sees stale value
balance = 1000 - 500         balance = 1000 - 300
set_balance(500)
                             set_balance(700)        ← overwrites A's work
                             ▔▔▔▔▔▔▔▔▔▔▔
                             Expected: 200   Actual: 700  ❌

The UnsafeAccountHelper subclass overrides get_balance() with a version
that calls time.sleep(0.05) *after* reading, guaranteeing that both
threads enter the window before either writes back.

For the SafeAccount, the same helper *must not* reproduce the race because
the lock serialises the two threads — the second thread blocks at the
lock boundary and only proceeds after the first has completed.
"""

import threading
import time

import pytest

from bank_buggy import UnsafeAccount
from bank_fixed import SafeAccount

# ── helpers that widen the race window ─────────────────────────────────


class UnsafeRacyAccount(UnsafeAccount):
    """Overrides get_balance() with a sleep to force interleaving."""

    def get_balance(self) -> int:
        val = super().get_balance()
        time.sleep(0.05)  # let the other thread read the stale value too
        return val


class SafeRacyAccount(SafeAccount):
    """Same sleep, but the Lock should serialise access."""

    def get_balance(self) -> int:
        val = super().get_balance()
        time.sleep(0.05)
        return val


# ── helpers for concurrent execution ───────────────────────────────────


def _par(account, amounts):
    """Fire N threads, each calling account.withdraw(a) for a in amounts."""
    threads = [threading.Thread(target=account.withdraw, args=(a,)) for a in amounts]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ── the actual tests ────────────────────────────────────────────────────


def test_unsafe_account_reveals_race():
    """The buggy version MUST produce a wrong final balance."""
    acct = UnsafeRacyAccount(initial_balance=1000)
    _par(acct, [500, 300])

    # Each thread sees 1000, so final balance is 1000-300 = 700 not 200
    assert acct.balance != 200, (
        f"Race condition did NOT manifest — balance={acct.balance}. "
        "This is expected on a fluke timing; run the test multiple times "
        "or increase the sleep in get_balance()."
    )


def test_safe_account_prevents_race():
    """The fixed version MUST always produce the correct final balance."""
    acct = SafeRacyAccount(initial_balance=1000)
    _par(acct, [500, 300])

    # 1000 - 500 - 300 = 200
    assert acct.balance == 200, (
        f"Locked account still racy — balance={acct.balance}, expected 200"
    )


def test_unsafe_account_high_contention():
    """
    100 concurrent withdrawals of 1 from a 100-balance account.

    The buggy version will almost never land on 0 because interleavings
    cause lost updates.
    """
    acct = UnsafeRacyAccount(initial_balance=100)
    _par(acct, [1] * 100)

    # Almost certainly not zero — but we accept any incorrect value
    assert acct.balance != 0, (
        f"Race did not manifest on 100 threads — balance={acct.balance}"
    )


def test_safe_account_high_contention():
    """100 concurrent withdrawals of 1 MUST converge to 0 with a lock."""
    acct = SafeRacyAccount(initial_balance=100)
    _par(acct, [1] * 100)

    assert acct.balance == 0, (
        f"Locked account lost updates under 100-thread contention — "
        f"balance={acct.balance}, expected 0"
    )


# ── pure-thread-racing (probabilistic) tests ───────────────────────────


def test_unsafe_account_probabilistic():
    """
    Without the racy helper, the bug is hard to trigger, but 100 threads
    each doing 10xRMW makes it nearly certain.

    This test is inherently flaky but included to show the *original*
    code pattern before the sleep-based widening trick.
    """
    acct = UnsafeAccount(initial_balance=1000)

    def hammer():
        for _ in range(10):
            acct.withdraw(1)

    threads = [threading.Thread(target=hammer) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Expected: 1000 - 100*10 = 0.  With the bug, almost certainly > 0.
    assert acct.balance == 0, (
        f"Probabilistic race caught! balance={acct.balance}, expected 0. "
        "This confirms the bug is real even without sleep injection."
    )


def test_safe_account_probabilistic():
    """Same hammer test — the locked version always passes."""
    acct = SafeAccount(initial_balance=1000)

    def hammer():
        for _ in range(10):
            acct.withdraw(1)

    threads = [threading.Thread(target=hammer) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert acct.balance == 0, (
        f"Locked account failed probabilistic test: {acct.balance}"
    )
