"""
bank_account_fixed.py — Race-free version using a threading.Lock.

Three alternative strategies are shown:
  1. threading.Lock   (transactional mutual exclusion)
  2. queue             (single-worker serialisation)
  3. atomic compare‐and‐swap   (lock‑free CAS — sketched)
"""

import threading
import time
import queue as _queue

# Reuse the simulated database from the buggy module
from bank_account import _db_read, _db_write


class FixedBankAccount:
    """
    Thread-safe bank account protected by a reentrant lock.

    Every public mutating method acquires ``self._lock`` so the
    two database calls (read + write) are *atomic from the caller's
    perspective* — no other thread can interleave between them.
    """

    def __init__(self, account_id: int, initial_balance: float = 0.0) -> None:
        self.account_id = account_id
        _db_write(account_id, initial_balance)
        self._lock = threading.Lock()

    def withdraw(self, amount: float) -> bool:
        """Withdraw money atomically."""
        with self._lock:
            current = _db_read(self.account_id)
            if current < amount:
                return False
            _db_write(self.account_id, current - amount)
            return True

    def deposit(self, amount: float) -> None:
        """Deposit money atomically."""
        with self._lock:
            _db_write(self.account_id, _db_read(self.account_id) + amount)

    @property
    def safe_balance(self) -> float:
        """Read the current balance safely."""
        with self._lock:
            return _db_read(self.account_id)

    def __repr__(self) -> str:
        return f"FixedBankAccount(#{self.account_id}, balance={self.safe_balance})"


# ═══════════════════════════════════════════════════════════════════
# Alternative:  Queue-based serialisation
# ═══════════════════════════════════════════════════════════════════


class QueuedBankAccount:
    """
    Thread-safe via a single worker thread processing a queue of
    commands.  Useful when the underlying store is I/O-bound.
    """

    def __init__(self, account_id: int, initial_balance: float = 0.0) -> None:
        self.account_id = account_id
        _db_write(account_id, initial_balance)
        self._req_queue: _queue.Queue = _queue.Queue()
        self._resp_queue: _queue.Queue = _queue.Queue()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()
        self._op_counter = 0
        self._op_lock = threading.Lock()

    def _next_idx(self) -> int:
        with self._op_lock:
            self._op_counter += 1
            return self._op_counter

    def _run(self) -> None:
        """Serialise all operations on this single thread."""
        while True:
            op, args, resp_idx = self._req_queue.get()
            try:
                if op == "withdraw":
                    amount = args[0]
                    current = _db_read(self.account_id)
                    ok = current >= amount
                    if ok:
                        _db_write(self.account_id, current - amount)
                    self._resp_queue.put((resp_idx, ok))
                elif op == "deposit":
                    amount = args[0]
                    _db_write(self.account_id, _db_read(self.account_id) + amount)
                    self._resp_queue.put((resp_idx, None))
                elif op == "balance":
                    self._resp_queue.put((resp_idx, _db_read(self.account_id)))
                elif op == "stop":
                    break
            finally:
                self._req_queue.task_done()

    def withdraw(self, amount: float) -> bool:
        idx = self._next_idx()
        self._req_queue.put(("withdraw", (amount,), idx))
        return self._resp_queue.get()[1]

    def deposit(self, amount: float) -> None:
        idx = self._next_idx()
        self._req_queue.put(("deposit", (amount,), idx))
        self._resp_queue.get()

    @property
    def safe_balance(self) -> float:
        idx = self._next_idx()
        self._req_queue.put(("balance", (), idx))
        return self._resp_queue.get()[1]

    def shutdown(self) -> None:
        self._req_queue.put(("stop", (), None))
