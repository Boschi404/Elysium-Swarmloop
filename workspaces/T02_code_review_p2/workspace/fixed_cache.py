"""
fixed_cache.py — FIX: LRU eviction + weak references.

Fixes demonstrated:
  1. Global cache → ``functools.lru_cache`` on a dedicated lookup function
     with a maxsize bound, plus optional ``@lru_cache`` for the fetcher.
  2. Event listeners → zero-arg listener stored via ``weakref.ref`` inside a
     ``WeakSet``-like container so subscribers can be GC'd when the caller
     drops its reference.
  3. Instance cache → ``WeakValueDictionary`` so cached instances are
     reclaimed when no strong reference exists.
"""

from __future__ import annotations

import functools
import weakref
from typing import Any, Callable


# ── Fix 1: LRU-cached data lookup ──────────────────────────────────────────

# Use functools.lru_cache with an explicit maxsize (LRU eviction).
# Avoids the unbounded global dict while preserving the caching benefit.
_MAX_CACHE_SIZE = 128


@functools.lru_cache(maxsize=_MAX_CACHE_SIZE)
def get_user_profile(user_id: str) -> dict[str, Any]:
    """Return a simulated user profile, cached with LRU eviction.

    The cache is bounded to ``_MAX_CACHE_SIZE`` entries.  When the limit
    is reached, the least-recently-used entry is evicted, preventing
    unbounded memory growth.
    """
    return _fetch_from_db(user_id)


def _fetch_from_db(user_id: str) -> dict[str, Any]:
    """Simulate a DB call — returns a moderately large dict."""
    import time

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


# ── Fix 2: Weak-reference-backed event listeners ──────────────────────────

from typing import Callable


class WeakListenerSet:
    """A container that holds weak references to callbacks.

    Callbacks are automatically removed when the referent is garbage
    collected.  This eliminates the orphaned-listener leak.
    """

    def __init__(self) -> None:
        self._refs: weakref.WeakMethod[Callable[[str], None] | None] = []

    def add(self, callback: Callable[[str], None]) -> None:
        # WeakMethod works for both bound methods and regular functions.
        # If `callback` is a plain function, weakref.ref is used as fallback.
        import weakref

        try:
            ref = weakref.WeakMethod(callback)
        except TypeError:
            # Plain function (not a bound method) → use ordinary weakref
            ref = weakref.ref(callback)
        self._refs.append(ref)
        # Sweep dead refs periodically to keep the list lean
        self._sweep()

    def _sweep(self) -> None:
        self._refs = [r for r in self._refs if r() is not None]

    def notify(self, message: str) -> None:
        for ref in list(self._refs):
            cb = ref()
            if cb is not None:
                cb(message)
        self._sweep()

    @property
    def alive_count(self) -> int:
        """Return number of still-alive listeners (for testing)."""
        return sum(1 for r in self._refs if r() is not None)


class DataBroadcaster:
    """Event emitter using weak references so subscribers can be GC'd."""

    def __init__(self) -> None:
        self._listeners = WeakListenerSet()

    def broadcast(self, message: str) -> None:
        self._listeners.notify(message)

    def subscribe(self, callback: Callable[[str], None]) -> None:
        self._listeners.add(callback)

    @property
    def subscriber_count(self) -> int:
        return self._listeners.alive_count


class DataConsumer:
    """Consumer that subscribes via WeakListenerSet — safe to discard."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.messages: list[str] = []

    def on_message(self, msg: str) -> None:
        self.messages.append(msg)


# ── Fix 3: WeakValueDictionary for instance cache ──────────────────────────

import weakref


class ExpensiveResourceFixed:
    """Instances cached via ``WeakValueDictionary``.

    When the caller drops the last strong reference to an instance, it is
    automatically removed from the cache and garbage collected.  No explicit
    ``__del__`` trickery required.
    """

    _instances: weakref.WeakValueDictionary[int, ExpensiveResourceFixed] = (
        weakref.WeakValueDictionary()
    )
    _counter = 0

    def __init__(self, data_size: int = 10_000) -> None:
        cls = self.__class__
        cls._counter += 1
        self.resource_id = cls._counter
        self.data = bytearray(data_size)
        # Register via WeakValueDictionary — does NOT prevent GC
        cls._instances[self.resource_id] = self


def demonstrate_fixes() -> dict[str, object]:
    """Run the same scenarios as leaky_cache.py but with fixes applied.

    Returns metrics showing the cache / listeners / instances behave
    correctly (zero orphaned references after scope exit).
    """
    # Fix 1: bounded LRU cache
    for i in range(100):
        get_user_profile(f"user_{i}")
    # Only _MAX_CACHE_SIZE entries remain
    cache_info = get_user_profile.cache_info()

    # Fix 2: weak listeners
    broadcaster = DataBroadcaster()
    consumers = [DataConsumer(f"consumer_{i}") for i in range(50)]
    for c in consumers:
        broadcaster.subscribe(c.on_message)
    # Consumers go out of scope — WeakListenerSet lets them be GC'd
    del consumers, c

    import gc

    gc.collect()
    alive_after_gc = broadcaster.subscriber_count

    # Fix 3: WeakValueDictionary
    resources = [ExpensiveResourceFixed() for _ in range(25)]
    del resources
    gc.collect()
    remaining_instances = len(ExpensiveResourceFixed._instances)

    return {
        "lru_cache_currsize": cache_info.currsize,
        "lru_cache_maxsize": cache_info.maxsize,
        "weak_listeners_alive": alive_after_gc,
        "weak_cache_remaining": remaining_instances,
        "resource_counter": ExpensiveResourceFixed._counter,
    }
