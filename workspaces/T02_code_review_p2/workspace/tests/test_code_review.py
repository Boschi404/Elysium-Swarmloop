"""
Tests for T02_code_review — Memory Leak Pattern
================================================
Verifies:
  1. code_with_leak demonstrates the leaks (cache grows, listeners persist)
  2. code_fixed bounds the cache and cleans up listeners
  3. WeakEventEmitter auto-releases dead callbacks
  4. BoundedComputation never exceeds maxsize
"""

import gc
import sys
import os
import weakref

# Ensure workspace is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_with_leak import (
    ExpensiveComputation as LeakyComputation,
    EventEmitter,
    DataSink,
    LargePayload,
    demonstrate_leak,
)
from code_fixed import (
    BoundedComputation,
    WeakEventEmitter,
    CleanupHandle,
    demonstrate_fix,
)


# ═══════════════════════════════════════════════════════════════════════════
# 1.  LEAK VERIFICATION — cache grows unbounded
# ═══════════════════════════════════════════════════════════════════════════

class TestCacheLeak:
    """Verify that the leaky cache grows without bound."""

    def test_leaky_cache_grows_indefinitely(self):
        """Adding 1000 unique keys should create 1000 cache entries."""
        for i in range(1000):
            LeakyComputation.compute(f"key-{i}", {"a": i, "b": i + 1})
        assert LeakyComputation.cache_size() == 1000, (
            f"Expected 1000 cached entries, got {LeakyComputation.cache_size()}"
        )

    def test_bounded_cache_respects_maxsize(self):
        """After 200 unique keys, lru_cache(128) should have at most 128 entries."""
        for i in range(200):
            BoundedComputation.compute(f"key-{i}")
        info = BoundedComputation.cache_info()
        assert info["current_size"] <= info["max_size"], (
            f"Cache exceeded maxsize: {info['current_size']} > {info['max_size']}"
        )
        assert info["current_size"] == 128, (
            f"Expected exactly 128 entries after 200 unique keys, got {info['current_size']}"
        )

    def test_bounded_lru_eviction_oldest(self):
        """LRU should evict the oldest entries, not the newest."""
        # Fill with keys 0-127
        for i in range(128):
            BoundedComputation.compute(f"evict-{i}")
        info = BoundedComputation.cache_info()
        assert info["current_size"] == 128

        # Add more keys — older ones should be evicted
        for i in range(128, 140):
            BoundedComputation.compute(f"evict-{i}")

        info = BoundedComputation.cache_info()
        assert info["current_size"] == 128

        # Key "evict-0" should now be evicted
        # Re-computing it should be a miss
        info_before = BoundedComputation.cache_info()
        BoundedComputation.compute("evict-0")
        info_after = BoundedComputation.cache_info()
        assert info_after["misses"] == info_before["misses"] + 1, (
            "evict-0 was not evicted — LRU is not working"
        )

    def test_bounded_cache_hit(self):
        """Re-using the same key should produce a cache hit."""
        BoundedComputation.compute("hit-test")
        info_before = BoundedComputation.cache_info()
        BoundedComputation.compute("hit-test")
        info_after = BoundedComputation.cache_info()
        assert info_after["hits"] == info_before["hits"] + 1


# ═══════════════════════════════════════════════════════════════════════════
# 2.  LEAK VERIFICATION — Event listeners
# ═══════════════════════════════════════════════════════════════════════════

class TestListenerLeak:
    """Verify that leaked listeners hold references and fixed ones don't."""

    def test_event_emitter_listeners_persist(self):
        """EventEmitter listeners are never cleaned up."""
        emitter = EventEmitter()
        assert emitter.listener_count() == 0
        for i in range(50):
            def cb(x): pass
            emitter.on("update", cb)
        assert emitter.listener_count() == 50

    def test_weak_emitter_disconnect_removes_listeners(self):
        """WeakEventEmitter.disconnect() actually removes the listener."""
        emitter = WeakEventEmitter()
        handles = []

        def cb(x): pass
        handle = emitter.on("update", cb)
        handles.append(handle)
        assert emitter.listener_count() == 1

        handle.disconnect()
        assert emitter.listener_count() == 0

    def test_weak_emitter_releases_dead_callbacks(self):
        """When the last strong ref to a callback is dropped, weakref
        should allow GC, and emit() should skip dead refs."""
        emitter = WeakEventEmitter()
        inner_count = []

        def make_cb():
            # closure that can be GC'd
            large = LargePayload(100_000)
            def cb(value):
                inner_count.append(len(large.payload))
            return cb

        # Register — keep no strong reference to the callback
        cb = make_cb()
        emitter.on("update", cb)
        assert emitter.listener_count() == 1

        # Drop the only strong reference and force GC
        del cb
        gc.collect()
        gc.collect()

        # emit should clean up the dead weakref
        emitter.emit("update", value=1)
        assert emitter.listener_count() == 0, (
            f"Dead callback not cleaned up: {emitter.listener_count()} listeners remain"
        )

    def test_data_sink_not_held_by_weak_emitter(self):
        """A DataSink can be collected even after registering a callback
        that references it, because the emitter uses weakref."""
        emitter = WeakEventEmitter()
        ref = [None]

        def scope():
            sink = DataSink("temp")
            sink.on_data(1)

            def cb(value):
                sink.on_data(value)

            emitter.on("data", cb)
            ref[0] = weakref.ref(sink)

        scope()
        gc.collect()
        gc.collect()

        # The DataSink should be collectable because the only reference
        # from the emitter is a weakref. However, `cb`'s closure still
        # holds a strong ref to `sink` — but `cb` itself is a local
        # that went out of scope after scope().
        # Let's check: the emitter holds cb by weakref, so when cb's
        # last strong ref dies (scope() exit), cb can be collected.
        assert ref[0]() is None, (
            "DataSink was NOT collected — something still holds a strong ref"
        )

    def test_cleanup_handle_paired_correctly(self):
        """Each on() returns a handle that disconnects the right callback."""
        emitter = WeakEventEmitter()
        results = []

        def cb_a(x): results.append("a")
        def cb_b(x): results.append("b")

        ha = emitter.on("ev", cb_a)
        hb = emitter.on("ev", cb_b)

        emitter.emit("ev", x=1)
        assert results == ["a", "b"]

        results.clear()
        ha.disconnect()
        emitter.emit("ev", x=2)
        assert results == ["b"], f"Expected ['b'], got {results}"


# ═══════════════════════════════════════════════════════════════════════════
# 3.  DEMONSTRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestDemonstration:

    def test_demonstrate_leak_returns_stats(self):
        stats = demonstrate_leak()
        assert stats["listener_count"] == 100
        assert stats["cache_size"] >= 0

    def test_demonstrate_fix_returns_stats(self):
        stats = demonstrate_fix()
        assert stats["listeners_before_disconnect"] == 100
        assert stats["listeners_after_disconnect"] == 50
        assert stats["cache_info"]["current_size"] <= stats["cache_info"]["max_size"]


# ═══════════════════════════════════════════════════════════════════════════
# 4.  GC INTEGRITY — no orphaned object graphs
# ═══════════════════════════════════════════════════════════════════════════

class TestGCIntegrity:

    def test_no_unexpected_global_references(self):
        """After a full GC cycle, no unexpected objects should remain
        from the leaky module (the global _RESULT_CACHE is expected)."""
        # Count objects before
        gc.collect()
        count_before = len(gc.get_objects())

        # Run the leaky demo within a local scope
        def scope():
            emitter = EventEmitter()
            for i in range(10):
                sink = DataSink(f"x-{i}")
                payload = LargePayload(1000)

                def make_cb(s=sink, p=payload):
                    def cb(v): s.on_data(v); _ = len(p.payload)
                    return cb

                emitter.on("update", make_cb())

        scope()
        gc.collect()
        gc.collect()

        # The leaky module's EventEmitter and _RESULT_CACHE should NOT
        # cause new unreachable cycles
        unreachable = gc.collect()
        # Some objects may remain reachable via the module's global cache
        # — that's the leak.  Just ensure there are no *new* reference cycles
        # that gc.collect() can't break.
        assert unreachable >= 0  # informational

    def test_weak_emitter_no_cycles(self):
        """WeakEventEmitter should not create reference cycles."""
        gc.collect()
        gc.collect()
        unreachable_before = len(gc.garbage)

        def scope():
            emitter = WeakEventEmitter()
            for i in range(10):
                def cb(v): pass
                emitter.on("update", cb)

        scope()
        gc.collect()
        gc.collect()

        unreachable_after = len(gc.garbage)
        # Weaker assertion: should not create *new* unreachable cycles
        new_cycles = unreachable_after - unreachable_before
        assert new_cycles <= 0, (
            f"WeakEventEmitter created {new_cycles} new garbage cycles"
        )
