"""
task_processor.py — SIMULATED CODE WITH MEMORY LEAKS.

This module intentionally contains memory leak patterns for code review.
Leak sources:
  1) Unbounded global cache dict
  2) Event listeners never unregistered
  3) Closure cycles keeping large objects alive
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ── LEAK 1: Unbounded global cache ──────────────────────────────────────────
# Every processed task result is appended here.  NEVER pruned.
_GLOBAL_CACHE: dict[str, Any] = {}
_cache_lock = threading.Lock()


def get_cached(key: str) -> Any | None:
    with _cache_lock:
        return _GLOBAL_CACHE.get(key)


def set_cached(key: str, value: Any) -> None:
    with _cache_lock:
        _GLOBAL_CACHE[key] = value


def clear_cache() -> None:
    with _cache_lock:
        _GLOBAL_CACHE.clear()


# ── LEAK 2: Event listener registry with no unsubscribe mechanism ──────────
_listeners: dict[str, list[Callable[..., None]]] = {}
_listener_lock = threading.Lock()


def register_listener(event: str, callback: Callable[..., None]) -> None:
    """Register a callback for an event.  No 'unregister' counterpart."""
    with _listener_lock:
        _listeners.setdefault(event, []).append(callback)


def emit(event: str, **kwargs: Any) -> None:
    with _listener_lock:
        for cb in _listeners.get(event, []):
            try:
                cb(event=event, **kwargs)
            except Exception:
                logger.exception("Listener %r failed for event %r", cb, event)


# ── LEAK 3: Closure capturing large objects in a processing pipeline ────────
class TaskProcessor:
    """Processes tasks and caches results — with built-in leaks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._history: list[dict[str, Any]] = []

    def process(self, task_data: dict[str, Any]) -> dict[str, Any]:
        result = self._do_process(task_data)
        # Store every result forever — no cap
        self._history.append(result)
        set_cached(f"{self.name}::{task_data.get('id', '?')}", result)
        return result

    def _do_process(self, data: dict[str, Any]) -> dict[str, Any]:
        # Simulate work
        return {"status": "done", "input": data, "output": data.get("value", 0) * 2}

    def on_event(self, event_name: str) -> Callable[[], None]:
        """Return a closure subscribed to an event.
        The closure captures 'self' even when the caller only needs the event.
        """
        def _handler(**_: Any) -> None:
            # Captures: self (full TaskProcessor), event_name (str)
            logger.info("[%s] handling event %s", self.name, event_name)
            self._history.append({"event": event_name})

        register_listener(event_name, _handler)
        return _handler


# ── LEAK 4: Callback accumulation from repetitive subscriptions ────────────
class LiveDataFeed:
    """Simulates a WebSocket / pub-sub feed."""

    def __init__(self, feed_id: str) -> None:
        self.feed_id = feed_id
        self._subscribers: list[Callable[[str], None]] = []

    def subscribe(self, callback: Callable[[str], None]) -> None:
        self._subscribers.append(callback)

    def push(self, message: str) -> None:
        for cb in self._subscribers:
            try:
                cb(message)
            except Exception:
                logger.exception("Subscriber failed")


# ── Usage example (run standalone for demonstration) ────────────────────────
def demonstrate_leaks() -> None:
    """Simulate repeated processing — every call leaks memory."""
    print("=== Memory Leak Demonstration ===")

    processors: list[TaskProcessor] = []
    for i in range(5):
        p = TaskProcessor(f"worker-{i}")
        processors.append(p)
        p.process({"id": f"job-{i}", "value": i * 10})

    feed = LiveDataFeed("market-data")
    for p in processors:
        feed.subscribe(lambda msg, proc=p: proc.process({"id": msg, "value": 1}))

    print(f"Global cache size: {len(_GLOBAL_CACHE)}")
    print(f"Listener count: {sum(len(v) for v in _listeners.values())}")
    print(f"Processor 0 history size: {len(processors[0]._history)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    demonstrate_leaks()
