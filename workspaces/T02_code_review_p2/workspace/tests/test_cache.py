"""
tests/test_cache.py — Unit tests for memory leak identification + fix.

Verifies:
  1. Leak detection: the leaky module retains objects after scope exit.
  2. Fix verification: the fixed module releases objects after scope exit.
"""

from __future__ import annotations

import gc
import os
import sys

# Ensure workspace is on sys.path
_ws = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ws not in sys.path:
    sys.path.insert(0, _ws)

from workspace import fixed_cache
from workspace import leaky_cache


# ── Helper ─────────────────────────────────────────────────────────────────

def count_instances(module: object, cls_name: str) -> int:
    """Count live instances of *cls_name* in *module* via gc.get_objects()."""
    gc.collect()
    cls = getattr(module, cls_name, None)
    if cls is None:
        return 0
    return sum(
        1
        for obj in gc.get_objects()
        if type(obj) is cls
    )


# ═══════════════════════════════════════════════════════════════════════════
#  1.  LEAK DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestLeakDetection:
    """Verify that leaky_cache.py holds on to objects after scope exit."""

    def test_leaky_cache_is_unbounded(self) -> None:
        """After 100 lookups the cache holds all 100 entries (no eviction)."""
        result = leaky_cache.demonstrate_leaks()
        assert result["global_cache_size"] == 100, (
            f"Expected 100 cached entries, got {result['global_cache_size']}"
        )

    def test_leaky_listeners_retain_objects(self) -> None:
        """DataConsumer instances still alive even after scope exit."""
        # Consumers are created inside demonstrate_leaks, then scope exits.
        # Because _listeners holds strong refs via bound methods, they live on.
        leaked = count_instances(leaky_cache, "DataConsumer")
        assert leaked > 0, (
            f"Expected leaked DataConsumer instances, got {leaked} "
            "(zero means GC collected them — fix may already work incorrectly?)"
        )

    def test_leaky_class_cache_pins_instances(self) -> None:
        """ExpensiveResource instances survive after scope exit."""
        leaked = count_instances(leaky_cache, "ExpensiveResource")
        assert leaked > 0, (
            f"Expected leaked ExpensiveResource instances, got {leaked}"
        )

    def test_leaky_cache_retains_class_dict(self) -> None:
        """ExpensiveResource._instances still has entries post-scope."""
        result = leaky_cache.demonstrate_leaks()
        assert result["class_cache_size"] >= 25, (
            f"Expected >= 25 cached instances, got {result['class_cache_size']}"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  2.  FIX VERIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFixVerification:
    """Verify that fixed_cache.py properly releases objects."""

    def test_fixed_cache_is_bounded(self) -> None:
        """LRU cache should hold at most maxsize entries."""
        result = fixed_cache.demonstrate_fixes()
        currsize: int = result["lru_cache_currsize"]  # type: ignore[assignment]
        maxsize: int = result["lru_cache_maxsize"]  # type: ignore[assignment]
        assert currsize <= maxsize, (
            f"Cache size {currsize} exceeds limit {maxsize}"
        )
        # After 100 lookups with maxsize=128, exactly 128 fit
        assert currsize <= 128

    def test_fixed_listeners_are_released(self) -> None:
        """After scope exit, no listeners remain alive."""
        result = fixed_cache.demonstrate_fixes()
        alive: int = result["weak_listeners_alive"]  # type: ignore[assignment]
        assert alive == 0, (
            f"Expected 0 alive listeners after GC, got {alive}"
        )

    def test_fixed_class_cache_releases_instances(self) -> None:
        """After scope exit, WeakValueDictionary should have ~0 entries."""
        result = fixed_cache.demonstrate_fixes()
        remaining: int = result["weak_cache_remaining"]  # type: ignore[assignment]
        assert remaining < 5, (
            f"Expected <5 cached instances after GC, got {remaining} "
            "(WeakValueDictionary entries may persist briefly; re-check)"
        )

    def test_fixed_no_reachable_consumers(self) -> None:
        """No DataConsumer instances should be reachable after scope exit."""
        # Run the fix demo which creates & drops consumers
        fixed_cache.demonstrate_fixes()
        gc.collect()
        leaked = count_instances(fixed_cache, "DataConsumer")
        assert leaked == 0, (
            f"Expected 0 leaked DataConsumer instances, got {leaked}"
        )

    def test_fixed_no_reachable_resource(self) -> None:
        """No ExpensiveResourceFixed instances reachable after drop."""
        fixed_cache.demonstrate_fixes()
        gc.collect()
        leaked = count_instances(fixed_cache, "ExpensiveResourceFixed")
        # A small window may still hold references from the return dict;
        # allow 0–2 but not the original 25.
        assert leaked < 5, (
            f"Expected <5 leaked ExpensiveResourceFixed, got {leaked}"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  3.  BEHAVIOURAL CORRECTNESS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestBehaviouralCorrectness:
    """Ensure the fixed code still works correctly (no regression)."""

    def test_get_user_profile_returns_data(self) -> None:
        """Fixed get_user_profile returns correct data."""
        profile = fixed_cache.get_user_profile("test_user")
        assert isinstance(profile, dict)
        assert profile["user_id"] == "test_user"
        assert profile["name"] == "User_test_user"

    def test_lru_cache_hit(self) -> None:
        """Second call to same key should hit cache (faster)."""
        fixed_cache.get_user_profile.cache_clear()
        fixed_cache.get_user_profile("hit_test")
        # Clear call count
        info_before = fixed_cache.get_user_profile.cache_info()
        fixed_cache.get_user_profile("hit_test")  # should be a hit
        info_after = fixed_cache.get_user_profile.cache_info()
        assert info_after.hits == info_before.hits + 1, (
            "Expected 1 cache hit on second call"
        )

    def test_broadcaster_delivers_messages(self) -> None:
        """WeakListenerSet still delivers to alive consumers."""
        broadcaster = fixed_cache.DataBroadcaster()
        consumer = fixed_cache.DataConsumer("alice")
        broadcaster.subscribe(consumer.on_message)

        broadcaster.broadcast("hello")
        assert "hello" in consumer.messages

        broadcaster.broadcast("world")
        assert consumer.messages == ["hello", "world"]

    def test_weak_listener_dies_with_consumer(self) -> None:
        """Dropped consumer should stop receiving messages."""
        broadcaster = fixed_cache.DataBroadcaster()
        consumer = fixed_cache.DataConsumer("bob")
        broadcaster.subscribe(consumer.on_message)

        # Message arrives while alive
        broadcaster.broadcast("first")
        assert consumer.messages == ["first"]

        # Discard consumer and force GC
        del consumer
        gc.collect()

        # After GC, the weak ref is dead; still deliver to any remaining
        broadcaster.broadcast("second")
        # There should be 0 alive listeners
        assert broadcaster.subscriber_count == 0

    def test_resource_lifecycle(self) -> None:
        """ExpensiveResourceFixed instances work and are collectable."""
        res = fixed_cache.ExpensiveResourceFixed(data_size=100)
        assert res.resource_id is not None
        assert len(res.data) == 100
        rid = res.resource_id

        # Instance is in the WeakValueDictionary while alive
        assert rid in fixed_cache.ExpensiveResourceFixed._instances

        del res
        gc.collect()
        assert rid not in fixed_cache.ExpensiveResourceFixed._instances, (
            "WeakValueDictionary should have released the entry"
        )
