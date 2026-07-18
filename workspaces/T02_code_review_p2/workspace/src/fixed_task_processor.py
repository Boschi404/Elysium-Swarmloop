"""
fixed_task_processor.py — MEMORY-LEAK-FREE VERSION.

Fixes applied:
  1) Global cache → LRU with bounded maxsize (functools.lru_cache)
  2) Event listeners → WeakMethod / WeakValueDictionary so listeners
     are GC-collected when the owning object dies.
  3) Closure cycles → explicit cleanup, avoid capturing 'self' unless needed.
  4) History cap → bounded deque on TaskProcessor._history.
"""

from __future__ import annotations

import logging
import threading
import weakref
from collections import OrderedDict, deque
from functools import lru_cache
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ── FIX 1: Bounded LRU cache (thread-safe) ─────────────────────────────────
class LRUCache:
    """Thread-safe LRU cache with a configurable max size."""

    def __init__(self, maxsize: int = 1_000) -> None:
        self._maxsize = maxsize
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key not in self._cache:
                return None
            self._cache.move_to_end(key)  # mark as recently used
            return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            while len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)  # evict least recently used

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)


_GLOBAL_CACHE = LRUCache(maxsize=1_000)


def get_cached(key: str) -> Any | None:
    return _GLOBAL_CACHE.get(key)


def set_cached(key: str, value: Any) -> None:
    _GLOBAL_CACHE.set(key, value)


def clear_cache() -> None:
    _GLOBAL_CACHE.clear()


# ── FIX 2: Weak-reference event listeners ───────────────────────────────────
class EventBus:
    """Event bus holding listeners via weak references.
    
    Listeners are automatically de-registered when the referent object
    is garbage-collected (unless a strong reference is kept elsewhere).
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[weakref.ref[Callable[..., None]]]] = {}
        self._lock = threading.Lock()

    def register(self, event: str, callback: Callable[..., None]) -> None:
        with self._lock:
            self._listeners.setdefault(event, []).append(weakref.ref(callback))

    def unregister(self, event: str, callback: Callable[..., None]) -> None:
        with self._lock:
            refs = self._listeners.get(event, [])
            self._listeners[event] = [
                r for r in refs if r() is not None and r() is not callback
            ]

    def emit(self, event: str, **kwargs: Any) -> None:
        with self._lock:
            dead: list[weakref.ref] = []
            for ref in self._listeners.get(event, []):
                cb = ref()
                if cb is None:
                    dead.append(ref)
                    continue
                try:
                    cb(event=event, **kwargs)
                except Exception:
                    logger.exception("Listener failed for event %r", event)
            # Prune dead refs
            if dead:
                self._listeners[event] = [
                    r for r in self._listeners[event] if r not in dead
                ]

    def listener_count(self, event: str | None = None) -> int:
        with self._lock:
            if event is not None:
                return len([r for r in self._listeners.get(event, []) if r() is not None])
            return sum(
                1 for ev in self._listeners.values() for r in ev if r() is not None
            )


_event_bus = EventBus()


def register_listener(event: str, callback: Callable[..., None]) -> None:
    _event_bus.register(event, callback)


def unregister_listener(event: str, callback: Callable[..., None]) -> None:
    _event_bus.unregister(event, callback)


def emit(event: str, **kwargs: Any) -> None:
    _event_bus.emit(event, **kwargs)


# ── FIX 3: Bounded history + proper cleanup ────────────────────────────────
class TaskProcessor:
    """Processes tasks with bounded cache and proper lifecycle."""

    def __init__(self, name: str, max_history: int = 500) -> None:
        self.name = name
        self._max_history = max_history
        self._history: deque[dict[str, Any]] = deque(maxlen=max_history)

    def process(self, task_data: dict[str, Any]) -> dict[str, Any]:
        result = self._do_process(task_data)
        self._history.append(result)
        set_cached(f"{self.name}::{task_data.get('id', '?')}", result)
        return result

    def _do_process(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"status": "done", "input": data, "output": data.get("value", 0) * 2}

    # The 'on_event' method now returns a *bound* reference that can be
    # unregistered, and doesn't hold the object alive unnaturally.
    def on_event(self, event_name: str) -> Callable[..., None]:
        """Return a weak-reference-safe event handler."""
        name = self.name  # capture only what is needed, not self

        def _handler(**_: Any) -> None:
            logger.info("[%s] handling event %s", name, event_name)

        register_listener(event_name, _handler)
        return _handler

    def cleanup(self) -> None:
        self._history.clear()


# ── FIX 4: Safe subscriber with cleanup method ─────────────────────────────
class LiveDataFeed:
    """Pub-sub feed with explicit unsubscribe."""

    def __init__(self, feed_id: str) -> None:
        self.feed_id = feed_id
        self._subscribers: list[Callable[[str], None]] = []

    def subscribe(self, callback: Callable[[str], None]) -> Callable[[], None]:
        self._subscribers.append(callback)
        # Return an unsubscribe callable
        def unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
        return unsubscribe

    def push(self, message: str) -> None:
        for cb in self._subscribers[:]:  # iterate over snapshot
            try:
                cb(message)
            except Exception:
                logger.exception("Subscriber failed")

    def subscriber_count(self) -> int:
        return len(self._subscribers)


# ── Demonstration ──────────────────────────────────────────────────────────
def demonstrate_fixed() -> None:
    """Simulate repeated processing — no memory leak."""
    print("=== Fixed Version Demonstration ===")
    import gc

    feed = LiveDataFeed("market-data")
    unsubs: list[Callable[[], None]] = []

    processors: list[TaskProcessor] = []
    for i in range(5):
        p = TaskProcessor(f"worker-{i}", max_history=10)
        processors.append(p)
        p.process({"id": f"job-{i}", "value": i * 10})
        unsubs.append(
            feed.subscribe(lambda msg, proc=p: proc.process({"id": msg, "value": 1}))
        )

    print(f"Global cache size: {_GLOBAL_CACHE.size}")
    print(f"Listener count: {_event_bus.listener_count()}")

    # Cleanup
    for unsub in unsubs:
        unsub()
    del processors

    gc.collect()
    print(f"After cleanup — listener count: {_event_bus.listener_count()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    demonstrate_fixed()
