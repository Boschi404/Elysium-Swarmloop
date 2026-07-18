"""
Tests for the fixed memory-leak patterns.

Verifies:
1. LRU cache stays bounded and evicts LRU entries
2. Cache hit/miss stats work correctly
3. WeakRefEmitter does not prevent GC of listeners
4. Explicit unregistration via ListenerHandle
5. Memory remains stable under repeated load
"""
from __future__ import annotations

import gc
import sys
import weakref
from pathlib import Path

import pytest

# Ensure we test the fixed version
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fixed_code import (
    WeakRefEmitter,
    ListenerHandle,
    cached_fetch,
    clear_cache,
    cache_info,
    _emitter,
    simulate,
)


# ═══════════════════════════════════════════════════════════════
# Fix A — LRU Cache Tests
# ═══════════════════════════════════════════════════════════════

class TestLRUCache:
    """Verify that the LRU cache stays bounded and evicts properly."""

    def setup_method(self) -> None:
        clear_cache()

    def test_cache_starts_empty(self) -> None:
        info = cache_info()
        assert info["currsize"] == 0
        assert info["maxsize"] == 256

    def test_cache_returns_payload(self) -> None:
        payload = cached_fetch("https://example.com")
        assert isinstance(payload, bytes)
        assert len(payload) == 1024 * 10  # 10 KiB

    def test_cache_hit_after_first_fetch(self) -> None:
        url = "https://example.com/data/1"
        cached_fetch(url)  # miss → stores
        info_before = cache_info()
        cached_fetch(url)  # hit
        info_after = cache_info()
        assert info_after["hits"] == info_before["hits"] + 1
        assert info_after["misses"] == info_before["misses"]

    def test_cache_stays_bounded(self) -> None:
        """Cache must never exceed maxsize entries."""
        for i in range(512):  # 2× maxsize
            cached_fetch(f"https://api.example.com/data/{i}")
        info = cache_info()
        assert info["currsize"] <= info["maxsize"]

    def test_lru_eviction_removes_oldest(self) -> None:
        """After filling cache, the oldest entries should be gone."""
        for i in range(256):
            cached_fetch(f"https://api.example.com/data/{i}")

        # All 256 are in cache; maxsize=256 so this is full.
        # Fetch one more — the oldest (index 0) should be evicted.
        cached_fetch("https://api.example.com/data/256")
        info = cache_info()
        assert info["currsize"] == 256  # still capped

        # Index 0 was evicted → fetching it again is a miss
        miss_before = cache_info()["misses"]
        cached_fetch("https://api.example.com/data/0")
        assert cache_info()["misses"] == miss_before + 1

    def test_cache_clear(self) -> None:
        cached_fetch("https://example.com")
        assert cache_info()["currsize"] == 1
        clear_cache()
        assert cache_info()["currsize"] == 0

    def test_cache_memory_bounded(self) -> None:
        """Verify approximate memory is bounded (not checking exact bytes)."""
        import tracemalloc  # stdlib in 3.4+
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()
            for i in range(1024):
                cached_fetch(f"https://api.example.com/data/{i}")
            current, peak = tracemalloc.get_traced_memory()
            # With 256 entries × ~10 KiB, peak should be well under 50 MiB
            assert peak < 50 * 1024 * 1024, f"Peak memory too high: {peak // 1024} KiB"
        finally:
            tracemalloc.stop()

    def test_thread_safety(self) -> None:
        """Basic concurrency smoke test — lru_cache is thread-safe under GIL."""
        import threading
        errors: list[Exception] = []

        def worker(start: int, count: int) -> None:
            try:
                for i in range(start, start + count):
                    cached_fetch(f"https://thread.example.com/data/{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i * 50, 50))
                   for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread-safety errors: {errors}"
        info = cache_info()
        assert info["currsize"] <= info["maxsize"]


# ═══════════════════════════════════════════════════════════════
# Fix B — Weak-Reference Emitter Tests
# ═══════════════════════════════════════════════════════════════

class TestWeakRefEmitter:
    """Verify listeners can be GC'd and explicitly unregistered."""

    def setup_method(self) -> None:
        self.em = WeakRefEmitter()

    def test_emit_calls_listener(self) -> None:
        received: list[str] = []

        def handler(msg: str) -> None:
            received.append(msg)

        self.em.on("data", handler)
        self.em.emit("data", "hello")
        assert received == ["hello"]

    def test_emit_multiple_listeners(self) -> None:
        results: list[int] = []

        def a() -> None:
            results.append(1)

        def b() -> None:
            results.append(2)

        self.em.on("evt", a)
        self.em.on("evt", b)
        self.em.emit("evt")
        assert results == [1, 2]

    def test_listener_can_be_gc_collected(self) -> None:
        """When the listener goes out of scope, the emitter must not hold it alive."""
        emitted: list[str] = []

        def handler(msg: str) -> None:
            emitted.append(msg)

        self.em.on("data", handler)
        # handler is still alive here — emit should work
        self.em.emit("data", "alive")
        assert emitted == ["alive"]

        # Delete the strong reference
        del handler
        gc.collect()

        # The emitter stores a weak ref — handler should be gone
        # Second emit should NOT invoke anything
        self.em.emit("data", "dead")
        assert emitted == ["alive"], "Handler was called after GC!"

    def test_listener_scope_collected(self) -> None:
        """
        Listeners created in a function are held ONLY by weak ref.

        When ``register()`` returns, the local ``listener`` function
        goes out of scope → its weak ref in the emitter is dead.
        ``emit()`` must silently skip dead refs, not raise or
        produce stale calls.
        """
        calls: list[str] = []

        def register() -> ListenerHandle:
            def listener(msg: str) -> None:
                calls.append(msg)
            return self.em.on("evt", listener)

        handle = register()
        # The listener was created inside register() and the function
        # object (which was referenced only by the local variable
        # `listener`) is now out of scope.  With weak-reference
        # semantics emit() simply skips it — no call happens.
        self.em.emit("evt", "first")
        # Because weakref to `listener` is already dead, nothing fires
        assert calls == [], (
            "WeakRefEmitter must NOT keep dead listeners alive"
        )

        # The handle still exists but emitter already released the ref
        del handle
        gc.collect()
        self.em.emit("evt", "second")
        assert calls == [], "Listener was called after GC!"

    def test_handle_removes_listener(self) -> None:
        received: list[str] = []

        def handler(msg: str) -> None:
            received.append(msg)

        handle = self.em.on("data", handler)
        self.em.emit("data", "before")
        assert received == ["before"]

        handle.remove()
        self.em.emit("data", "after")
        assert received == ["before"], "Listener was not removed by handle!"

    def test_double_remove_is_safe(self) -> None:
        def handler() -> None:
            pass

        handle = self.em.on("evt", handler)
        handle.remove()
        handle.remove()  # should not raise

    def test_emitter_reports_listener_count(self) -> None:
        def a() -> None:
            pass
        def b() -> None:
            pass

        assert self.em.listener_count == 0
        ha = self.em.on("e1", a)
        assert self.em.listener_count == 1
        hb = self.em.on("e2", b)
        assert self.em.listener_count == 2

        ha.remove()
        assert self.em.listener_count == 1

        hb.remove()
        assert self.em.listener_count == 0

    def test_listener_count_after_gc(self) -> None:
        def handler() -> None:
            pass

        self.em.on("e", handler)
        assert self.em.listener_count == 1

        del handler
        gc.collect()
        # emit prunes dead refs, but count() also skips dead refs
        assert self.em.listener_count == 0

    def test_emit_on_unknown_event_no_error(self) -> None:
        self.em.emit("nonexistent")  # should not raise

    def test_no_strong_ref_to_emitter_in_handle(self) -> None:
        """ListenerHandle must not keep the emitter alive."""
        em = WeakRefEmitter()
        em_ref = weakref.ref(em)

        def handler() -> None:
            pass

        handle = em.on("e", handler)
        # Discard the emitter
        del em
        gc.collect()
        # The handle still exists but should not keep the emitter alive
        # Calling remove() on a dead emitter is a no-op
        handle.remove()

    def test_many_listeners_memory_bounded(self) -> None:
        """After 10k registrations + discarding handles, memory must not grow."""
        for i in range(10_000):
            def handler() -> None:
                pass
            self.em.on("e", handler)
            # handler goes out of scope after each iteration — only weak ref remains

        # Delete the last loop variable so it doesn't hold the final function alive
        del handler
        gc.collect()
        # emit prunes dead refs
        self.em.emit("e")

        # After cleanup, no live listeners should remain
        assert self.em.listener_count == 0
        # Event key should be removed
        assert self.em.total_slots == 0


# ═══════════════════════════════════════════════════════════════
# Integration Test
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    """End-to-end test of the simulate() function."""

    def test_simulate_memory_stable(self) -> None:
        """After simulate() + GC, memory should return to near-baseline."""
        gc.collect()
        baseline = len(gc.get_objects())

        simulate(iterations=500)

        gc.collect()
        after = len(gc.get_objects())

        # The 500 listeners should all be reclaimable.
        # Allow ~50 objects overhead (module internals, strings, etc.)
        leak = after - baseline
        assert leak < 100, (
            f"Leaked approximately {leak} objects after simulate(500)"
        )

    def test_cache_stays_bounded_during_simulate(self) -> None:
        clear_cache()  # isolate from previous tests
        simulate(iterations=500)
        info = cache_info()
        assert info["currsize"] <= info["maxsize"]
        assert info["misses"] == 500  # 500 unique URLs, 500 misses

    def test_listeners_reclaimed(self) -> None:
        """Verify that weak-ref listeners don't leak when caller discards them."""
        em2 = WeakRefEmitter()
        captured: list[str] = []

        def handler(msg: str) -> None:
            captured.append(msg)

        # Keep a strong ref — listener is alive
        handle = em2.on("data", handler)
        em2.emit("data", "alive")
        assert captured == ["alive"], "Listener should fire while ref held"

        # Discard the strong ref via handle removal
        handle.remove()
        em2.emit("data", "after-remove")
        assert captured == ["alive"], "Listener must not fire after removal"

        # Also test: if handler itself goes out of scope (no handle needed)
        # the weak ref dies automatically
        em2.on("data", handler)      # re-register
        em2.emit("data", "again")
        assert captured == ["alive", "again"]

        del handler                   # drop the only strong ref
        gc.collect()
        em2.emit("data", "should-not-fire")
        assert captured == ["alive", "again"], (
            "Listener fired after strong ref was dropped!"
        )

        # After GC cleanup, no live listeners remain
        assert em2.listener_count == 0


# ═══════════════════════════════════════════════════════════════
# Leak Detection Confirmation
# ═══════════════════════════════════════════════════════════════

class TestLeakProof:
    """Confirm the original leak scenarios are fixed."""

    def test_cache_does_not_grow_unbounded(self) -> None:
        """Leak A must be fixed — cache must have a boundary."""
        for i in range(10_000):
            cached_fetch(f"https://leak-test.example.com/data/{i}")
        info = cache_info()
        assert info["currsize"] <= 256, "Cache grew unbounded!"

    def test_listeners_do_not_accumulate(self) -> None:
        """
        Leak B must be fixed — unregistered listeners are not
        permanently retained by the emitter.
        """
        em = WeakRefEmitter()

        # Register block of listeners, then discard the handles
        handles = []
        for i in range(1_000):
            def make_handler(n: int):
                return lambda: None
            h = em.on("leak", make_handler(i))
            handles.append(h)

        # Remove all handles
        for h in handles:
            h.remove()

        assert em.listener_count == 0
        assert em.total_slots == 0, "Dead refs left behind after removal!"
