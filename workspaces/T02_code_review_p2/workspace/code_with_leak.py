"""
T02_code_review — Memory Leak Pattern: Leaky Example
=====================================================
Demonstrates two classic Python memory leak patterns:
  1. Unbounded global cache dict (grows forever)
  2. Event listeners that are registered but never removed
"""

import time
import gc
import sys
from typing import Any, Callable


# ── LEAK PATTERN #1: Unbounded Global Cache ────────────────────────────────

_RESULT_CACHE: dict[str, Any] = {}
"""Global cache that grows unbounded — entries are NEVER evicted."""


class ExpensiveComputation:
    """Simulates a computation-heavy operation whose results are cached."""

    @classmethod
    def compute(cls, key: str, data: dict) -> dict:
        """Return cached result or compute and store — but NEVER cleans up."""
        if key in _RESULT_CACHE:
            return _RESULT_CACHE[key]

        # Simulate expensive work
        result = {k: v ** 2 for k, v in data.items()}
        _RESULT_CACHE[key] = result       # <-- LEAK: never removed
        return result

    @classmethod
    def cache_size(cls) -> int:
        return len(_RESULT_CACHE)


# ── LEAK PATTERN #2: Event Listeners Never Removed ─────────────────────────

class EventEmitter:
    """Simple pub/sub where subscribers are stored by strong reference."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}
        """LISTS hold strong references to listener callables — LEAK."""

    def on(self, event: str, callback: Callable) -> None:
        """Register a listener.  No way to unregister!"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)   # <-- LEAK: strong ref, never removed

    def emit(self, event: str, **kwargs) -> None:
        """Fire an event to all registered listeners."""
        for cb in self._listeners.get(event, []):
            cb(**kwargs)

    def listener_count(self) -> int:
        return sum(len(v) for v in self._listeners.values())


# ── DEMONSTRATION UTILITY ──────────────────────────────────────────────────

class DataSink:
    """An object we attach listeners to — simulates a UI controller, DB
    connection, or similar long-lived object whose lifecycle should be tied
    to listener cleanup."""

    def __init__(self, name: str):
        self.name = name
        self._data: list[int] = []

    def on_data(self, value: int) -> None:
        self._data.append(value)

    def __repr__(self) -> str:
        return f"<DataSink {self.name}>"


class LargePayload:
    """A heavyweight object that would be held alive by a leaked callback
    closure — simulates a UI widget, network connection, or big data frame."""

    def __init__(self, size: int = 1_000_000):
        self.payload = bytearray(size)   # ~1 MB

    def __repr__(self) -> str:
        return f"<LargePayload {id(self):#x}>"


# ── CONCRETE LEAK DEMO: callback closure captures LargePayload ──────────────

def demonstrate_leak() -> dict:
    """Run the leaky scenario and return stats."""
    emitter = EventEmitter()
    sinks: list[DataSink] = []

    # Register listeners that capture large objects via closure
    for i in range(100):
        sink = DataSink(f"sink-{i}")
        payload = LargePayload()            # ~1 MB each
        sinks.append(sink)

        # Closure captures `sink` and `payload` by strong reference
        def make_cb(s=sink, p=payload):
            def cb(value: int) -> None:
                s.on_data(value)
                _ = len(p.payload)          # keep payload alive
            return cb

        emitter.on("update", make_cb())
        # NOTE: sink & payload remain referenced by the closure even after
        #       `sinks` list is discarded — because the listener list holds
        #       the callback, and the callback holds `s` and `p`.

    # Fire once
    emitter.emit("update", value=42)

    return {
        "listener_count": emitter.listener_count(),
        "cache_size": ExpensiveComputation.cache_size(),
    }


if __name__ == "__main__":
    stats = demonstrate_leak()
    print(f"Listeners: {stats['listener_count']}")
    print(f"Cache entries: {stats['cache_size']}")
    print("---")
    print("Run 'python code_fixed.py' to see the fix")
