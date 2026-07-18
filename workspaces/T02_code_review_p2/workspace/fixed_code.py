"""
fixed_code.py — Memory-leak-free versions of both patterns.

Fix A: @functools.lru_cache(maxsize=256) — bounded LRU eviction.
Fix B: WeakRefEmitter — weak-reference listeners + ListenerHandle for explicit
       unregistration; dead references pruned lazily during emit().
"""
from __future__ import annotations

import functools
import gc
import sys
import weakref
from typing import Any, Callable, Optional

# ──────────────────────────────────────────────────────────────
# FIX A — LRU-cached fetch (bounded, auto-eviction)
# ──────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=256)
def cached_fetch(url: str) -> bytes:
    """
    Fetch URL content with a bounded LRU cache.

    At most 256 entries live in cache.  When a new entry is added past
    the limit, the *least recently used* entry is evicted.

    Returns a 10 KiB simulated payload for testing.
    """
    return b"x" * 1024 * 10


def clear_cache() -> None:
    """Programmatic cache flush (same interface as leaky version)."""
    cached_fetch.cache_clear()


def cache_info() -> dict[str, int]:
    """Return cache stats (hits, misses, maxsize, currsize)."""
    info = cached_fetch.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "maxsize": info.maxsize,
        "currsize": info.currsize,
    }


# ──────────────────────────────────────────────────────────────
# FIX B — Weak-reference event emitter with clean unregistration
# ──────────────────────────────────────────────────────────────

class ListenerHandle:
    """
    Opaque handle returned by WeakRefEmitter.on().

    The caller keeps (or discards) this handle.  When they want to
    unregister, they call handle.remove().  If the handle itself is
    garbage-collected first, the emitter lazily prunes the dead ref
    on the next emit().
    """

    def __init__(
        self,
        emitter: "WeakRefEmitter",
        event: str,
        ref: weakref.ref,
    ) -> None:
        self._emitter_ref = weakref.ref(emitter)
        self._event = event
        self._ref = ref

    def remove(self) -> None:
        """Unregister the associated listener (idempotent)."""
        em = self._emitter_ref()
        if em is not None:
            em._remove(self._event, self._ref)
        # After removal, clear the internal ref so double-remove is safe
        self._ref = None  # type: ignore[assignment]


class WeakRefEmitter:
    """
    Event emitter that stores listeners as weak references.

    - Listeners are stored as ``weakref.ref`` objects.
    - Dead references are pruned on every ``emit()`` (lazy cleanup).
    - ``on()`` returns a ``ListenerHandle`` for explicit unregistration.
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[weakref.ref]] = {}

    def on(self, event: str, listener: Callable[..., Any]) -> ListenerHandle:
        """
        Register *listener* for *event*.

        Returns a ``ListenerHandle`` that the caller can use to
        unregister later.
        """
        ref = weakref.ref(listener)
        self._listeners.setdefault(event, []).append(ref)
        return ListenerHandle(self, event, ref)

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Fire *event* to all live listeners.

        Dead (garbage-collected) listeners are pruned during iteration.
        If no listeners remain the event key is removed.
        """
        refs = self._listeners.get(event)
        if refs is None:
            return

        live: list[weakref.ref] = []
        for ref in refs:
            listener = ref()
            if listener is not None:
                listener(*args, **kwargs)
                live.append(ref)

        if live:
            self._listeners[event] = live
        else:
            # No more live listeners for this event → clean up the key
            self._listeners.pop(event, None)

    def _remove(self, event: str, ref: Optional[weakref.ref]) -> None:
        """Remove a specific weak reference from the listener list."""
        refs = self._listeners.get(event)
        if refs is None:
            return
        try:
            refs.remove(ref)
        except ValueError:
            pass
        if not refs:
            self._listeners.pop(event, None)

    @property
    def listener_count(self) -> int:
        """Return number of *live* listeners across all events."""
        total = 0
        for refs in self._listeners.values():
            total += sum(1 for r in refs if r() is not None)
        return total

    @property
    def total_slots(self) -> int:
        """Return total stored references (including dead ones)."""
        return sum(len(v) for v in self._listeners.values())


# Module-level emitter for convenience (same interface as leaky version)
_emitter = WeakRefEmitter()


def subscribe_forever(source: str) -> ListenerHandle:
    """
    Register a listener that captures *source*.

    Because the emitter stores a **weak** reference, the closure and
    its captured ``source`` can be garbage-collected when the caller
    discards the returned handle or when the handle itself goes out
    of scope.
    """

    def on_data(payload: Any) -> None:
        _ = f"[{source}] received {payload}"

    return _emitter.on("data", on_data)


# ──────────────────────────────────────────────────────────────
# Measurement helpers
# ──────────────────────────────────────────────────────────────

def leak_report() -> str:
    """Return a human-readable report of current memory state."""
    ci = cache_info()
    live_listeners = _emitter.listener_count
    return (
        f"Fix A — Cache entries: {ci['currsize']}/{ci['maxsize']}  "
        f"(hits={ci['hits']}, misses={ci['misses']})\n"
        f"Fix B — Live listeners: {live_listeners}\n"
        f"GC tracked objects: {len(gc.get_objects())}"
    )


def simulate(iterations: int = 200) -> None:
    """Run a simulation against the fixed code."""
    handles: list[ListenerHandle] = []
    for i in range(iterations):
        cached_fetch(f"https://api.example.com/data/{i:06d}")
        h = subscribe_forever(f"sensor-{i:04d}")
        handles.append(h)

    # Demonstrate that we can unregister listeners
    for h in handles:
        h.remove()

    # Re-register only a few
    for i in range(5):
        subscribe_forever(f"remaining-sensor-{i:04d}")


if __name__ == "__main__":
    BEFORE = leak_report()
    simulate(500)
    gc.collect()
    AFTER = leak_report()
    print("BEFORE:")
    print(BEFORE)
    print("\nAFTER (500 iterations, all handles removed + GC):")
    print(AFTER)
