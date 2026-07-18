"""
leaky_code.py — Code with TWO memory leaks for review:

Leak A: Unbounded global cache dict (dictionary-backed, no eviction)
Leak B: Strong-reference event listener registry (listeners never unregistered)

Run `python leaky_code.py` to observe growth.
Run `python -c "import leaky_code; print(leaky_code.leak_report())"` for stats.
"""
from __future__ import annotations

import gc
import sys
import threading
from typing import Any, Callable

# ──────────────────────────────────────────────────────────────
# LEAK A — Unbounded global cache (dict, no max size, no eviction)
# ──────────────────────────────────────────────────────────────
_CACHE: dict[str, bytes] = {}          # ← the leak: grows forever

def cached_fetch(url: str) -> bytes:
    """Simulate a cached fetch — stores every URL in an unbounded dict."""
    if url in _CACHE:
        return _CACHE[url]
    # simulate a payload
    payload = b"x" * 1024 * 10          # 10 KiB per entry
    _CACHE[url] = payload               # ← never removed, cache grows unbounded
    return payload


def clear_cache() -> None:
    """Manually clear the cache (never called in production flow)."""
    _CACHE.clear()

# ──────────────────────────────────────────────────────────────
# LEAK B — Strong-reference event listeners never unregistered
# ──────────────────────────────────────────────────────────────

class EventEmitter:
    """Event emitter that stores listener references — and never removes them."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    def on(self, event: str, listener: Callable[..., Any]) -> None:
        """Register a listener (strong reference stored)."""
        self._listeners.setdefault(event, []).append(listener)
        # ← BUG: no way to unregister; even one-shot listeners live forever

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        for listener in self._listeners.get(event, []):
            listener(*args, **kwargs)

    @property
    def listener_count(self) -> int:
        return sum(len(v) for v in self._listeners.values())


_emitter = EventEmitter()

def subscribe_forever(source: str) -> None:
    """Register a listener that holds a strong reference to its closure scope."""
    def on_data(payload: Any) -> None:
        # each closure captures `source` and keeps it alive
        _ = f"[{source}] received {payload}"

    _emitter.on("data", on_data)          # ← listener is never removed
    # every call to subscribe_forever creates a NEW closure and appends it


# ──────────────────────────────────────────────────────────────
# Measurement helpers
# ──────────────────────────────────────────────────────────────

def leak_report() -> str:
    """Return a human-readable report of current memory state."""
    cache_size = sum(sys.getsizeof(v) for v in _CACHE.values()) + \
                 sum(sys.getsizeof(k) for k in _CACHE)
    return (
        f"Leak A — Cache entries: {len(_CACHE)}  (approx {cache_size // 1024} KiB)\n"
        f"Leak B — Listeners registered: {_emitter.listener_count}\n"
        f"GC tracked objects: {len(gc.get_objects())}"
    )


def simulate_leak(iterations: int = 200) -> None:
    """Run a simulation that exercises both leak paths."""
    for i in range(iterations):
        # Leak A: unique URLs every time
        cached_fetch(f"https://api.example.com/data/{i:06d}")
        # Leak B: new listener every time
        subscribe_forever(f"sensor-{i:04d}")


if __name__ == "__main__":
    BEFORE = leak_report()
    simulate_leak(500)
    AFTER = leak_report()
    print("BEFORE:")
    print(BEFORE)
    print("\nAFTER (500 iterations):")
    print(AFTER)
