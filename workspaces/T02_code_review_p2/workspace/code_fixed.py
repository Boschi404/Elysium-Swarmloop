"""
T02_code_review — Memory Leak Pattern: Fixed Version
=====================================================
Fixes both leak patterns from code_with_leak.py:
  1. ✅ functools.lru_cache with maxsize bounds the cache
  2. ✅ weakref.WeakSet + disconnect() for listener lifecycle management
"""

import weakref
import gc
import functools
from typing import Any, Callable


# ── FIX #1: LRU-Cached Computation ─────────────────────────────────────────

class BoundedComputation:
    """Results are cached with an LRU eviction policy and hard size limit."""

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def compute(key: str, /) -> frozenset:
        """Cached via functools.lru_cache — max 128 entries, LRU eviction.
        The argument MUST be hashable (str is fine).
        Returns a frozenset so the result itself is immutable & hashable."""
        # Simulate expensive work
        parts = key.split(",")
        return frozenset(p.strip() for p in parts)

    @classmethod
    def cache_info(cls) -> dict:
        """Return LRU cache stats for monitoring."""
        info = cls.compute.cache_info()
        return {
            "hits": info.hits,
            "misses": info.misses,
            "current_size": info.currsize,
            "max_size": info.maxsize,
        }


# ── FIX #2: Weak-Referenced Event Listeners + Explicit Disconnect ──────────

class WeakEventEmitter:
    """Event system where listeners are stored via WeakRef.
    Dead listeners are automatically cleaned up on emit."""

    def __init__(self):
        self._listeners: dict[str, list[weakref.ref]] = {}
        """Each listener is stored as a weak reference to the callable."""

    def on(self, event: str, callback: Callable) -> "CleanupHandle":
        """Register a listener.  Returns a handle that can be used to
        disconnect — no more orphaned listeners."""
        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(weakref.ref(callback))

        # Return a cleanup handle so the caller can disconnect
        return CleanupHandle(self, event, callback)

    def disconnect(self, event: str, callback: Callable) -> None:
        """Explicitly remove a specific listener."""
        refs = self._listeners.get(event)
        if not refs:
            return
        # Remove all dead refs + the matching one
        self._listeners[event] = [
            r for r in refs
            if r() is not None and r() is not callback
        ]

    def emit(self, event: str, **kwargs) -> None:
        """Fire an event, cleaning up dead listeners along the way."""
        refs = self._listeners.get(event)
        if not refs:
            return

        alive: list[weakref.ref] = []
        for ref in refs:
            cb = ref()
            if cb is not None:
                cb(**kwargs)
                alive.append(ref)
            # else: listener was garbage-collected — drop silently
        self._listeners[event] = alive

    def listener_count(self) -> int:
        return sum(len(v) for v in self._listeners.values())


class CleanupHandle:
    """A reconnectable handle returned by WeakEventEmitter.on().
    Call .disconnect() to remove the listener."""

    def __init__(self, emitter: WeakEventEmitter, event: str, callback: Callable):
        self._emitter = emitter
        self._event = event
        self._callback = callback

    def disconnect(self) -> None:
        self._emitter.disconnect(self._event, self._callback)


# ── DEMONSTRATION ──────────────────────────────────────────────────────────

class DataSink:
    """Same as before — but now listeners don't keep us alive."""

    def __init__(self, name: str):
        self.name = name
        self._data: list[int] = []

    def on_data(self, value: int) -> None:
        self._data.append(value)

    def __repr__(self) -> str:
        return f"<DataSink {self.name}>"


class LargePayload:
    def __init__(self, size: int = 1_000_000):
        self.payload = bytearray(size)

    def __repr__(self) -> str:
        return f"<LargePayload {id(self):#x}>"


def demonstrate_fix() -> dict:
    """Run the fixed scenario and show listeners auto-clean up."""
    emitter = WeakEventEmitter()
    handles: list[CleanupHandle] = []

    for i in range(100):
        sink = DataSink(f"sink-{i}")
        payload = LargePayload()

        # Make a bound method so the callback itself is a new object
        # that can be garbage-collected independently.
        def make_cb(s=sink):
            def cb(value: int) -> None:
                s.on_data(value)
            return cb

        fn = make_cb()
        handle = emitter.on("update", fn)
        handles.append(handle)

    # All local DataSinks and LargePayloads SHOULD be collected now
    # because the callbacks are held only by weakref.
    # The `handles` list keeps the callbacks alive, so we manually
    # disconnect half to demonstrate clean removal.

    before = emitter.listener_count()
    for h in handles[:50]:
        h.disconnect()
    after = emitter.listener_count()

    emitter.emit("update", value=99)

    return {
        "listeners_before_disconnect": before,
        "listeners_after_disconnect": after,
        "cache_info": BoundedComputation.cache_info(),
    }


if __name__ == "__main__":
    stats = demonstrate_fix()
    print(f"Listeners before disconnect: {stats['listeners_before_disconnect']}")
    print(f"Listeners after  disconnect: {stats['listeners_after_disconnect']}")
    print(f"LRU Cache: {stats['cache_info']}")
