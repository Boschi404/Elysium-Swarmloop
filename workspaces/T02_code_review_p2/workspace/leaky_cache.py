"""
leaky_cache.py — DEMO: Code with deliberate memory leak patterns.

Two leak sources:
  1. A global _CACHE dict that grows unbounded (no eviction policy).
  2. Event listeners stored in a global list that are never removed,
     preventing GC of the listener objects and everything they reference.
"""

from __future__ import annotations

import dataclasses
import sys
import time
from typing import Any, Callable


# ── Leak Source 1: Unbounded global cache ──────────────────────────────────

_CACHE: dict[str, Any] = {}

EXPENSIVE_DATA_STORE: dict[int, bytes] = {}


def get_user_profile(user_id: str) -> dict[str, Any]:
    """Return a simulated user profile.

    ⚠️  Leak: every unique *user_id* is cached permanently in _CACHE.
        The dict grows without bound, consuming memory for every user that
        has ever been looked up.
    """
    if user_id not in _CACHE:
        # Simulate an expensive operation
        profile = _fetch_from_db(user_id)
        _CACHE[user_id] = profile
    return _CACHE[user_id]


def _fetch_from_db(user_id: str) -> dict[str, Any]:
    """Simulate a DB call — returns a moderately large dict."""
    # Simulate ~4 KB per profile — enough to make the leak measurable
    return {
        "user_id": user_id,
        "name": f"User_{user_id}",
        "email": f"{user_id}@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en",
        },
        "metadata": {
            "created_at": time.time(),
            "last_login": time.time() - 3600,
            "profile_views": 42,
            "tags": ["premium", "beta", "vip", "early_adopter"],
        },
        "address": {
            "street": "123 Memory Leak Ave",
            "city": "Cacheville",
            "zip": "00000",
            "country": "Leakland",
        },
    }


# ── Leak Source 2: Orphaned event listeners ────────────────────────────────

_listeners: list[Callable[[], None]] = []


class DataBroadcaster:
    """An event emitter that NEVER unregisters listeners.

    ⚠️  Every call to *subscribe* appends a callback to a global list.
        The list holds a strong reference to the bound method of the
        subscriber, preventing the subscriber object from being GC'd.
    """

    def broadcast(self, message: str) -> None:
        for listener in _listeners:
            listener(message)

    def subscribe(self, callback: Callable[[str], None]) -> None:
        _listeners.append(callback)


class DataConsumer:
    """Consumer that subscribes to DataBroadcaster.

    When a *DataConsumer* instance subscribes, *subscribe* stores
    `self.on_message` — a bound method holding a strong ref to ``self``.
    If the consumer is later discarded (goes out of scope), the reference
    in _listeners keeps it alive → **memory leak**.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.messages: list[str] = []

    def on_message(self, msg: str) -> None:
        self.messages.append(msg)


# ── Leak Source 3 (bonus): class-level cache preventing GC ─────────────────

class ExpensiveResource:
    """Instances hold a large blob and are cached by class-level dict.

    ⚠️  The class-level dict ``ExpensiveResource._instances`` maps
        resource *id* → instance, creating a strong reference chain that
        prevents the instance from being garbage collected even when the
        caller has no reference to it.
    """

    _instances: dict[int, ExpensiveResource] = {}
    _counter = 0

    def __init__(self, data_size: int = 10_000) -> None:
        cls = self.__class__
        cls._counter += 1
        self.resource_id = cls._counter
        # Large blob of data (~8 KB per instance)
        self.data = bytearray(data_size)
        # Self-register — this instance is now pinned forever
        cls._instances[self.resource_id] = self

    def __del__(self) -> None:
        # Note: even __del__ won't help because _instances holds the ref
        print(f"ExpensiveResource#{self.resource_id} collected", file=sys.stderr)


def demonstrate_leaks() -> dict[str, object]:
    """Run several leak scenarios and return metrics.

    Returns a dict with object counts so the test can verify leaks exist.
    """
    # Leak 1: unbounded global cache
    for i in range(100):
        get_user_profile(f"user_{i}")

    # Leak 2: orphaned listeners
    broadcaster = DataBroadcaster()
    consumers = [DataConsumer(f"consumer_{i}") for i in range(50)]
    for c in consumers:
        broadcaster.subscribe(c.on_message)
    # consumers go out of scope here, but _listeners keeps them alive

    # Leak 3: class-level cache
    resources = [ExpensiveResource() for _ in range(25)]
    # resources goes out of scope here, but _instances keeps them alive

    return {
        "global_cache_size": len(_CACHE),
        "listener_count": len(_listeners),
        "class_cache_size": len(ExpensiveResource._instances),
        "class_counter": ExpensiveResource._counter,
    }
