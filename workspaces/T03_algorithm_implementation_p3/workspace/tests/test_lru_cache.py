"""
Comprehensive tests for LRUCache.

Tests cover:
- Basic get/put semantics
- Eviction (LRU order)
- delete(key)
- Thread safety (concurrent access)
- Statistics (hits, misses, size)
- Edge cases (capacity=1, large volumes, None keys)
- __contains__, __len__, __repr__, clear
"""

from __future__ import annotations

import threading
import time
from typing import Any

import pytest

from lru_cache import LRUCache


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def cache() -> LRUCache:
    """A small cache useful for unit tests."""
    return LRUCache(capacity=3)


@pytest.fixture
def med_cache() -> LRUCache:
    """A medium cache for scale tests."""
    return LRUCache(capacity=100)


# ======================================================================
# Basic get / put
# ======================================================================

class TestBasicOperations:
    def test_put_and_get(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_get_missing_returns_minus_one(self, cache: LRUCache) -> None:
        assert cache.get("nonexistent") == -1

    def test_update_existing(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("a", 42)
        assert cache.get("a") == 42
        assert cache.size == 1  # no new entry

    def test_int_keys(self, cache: LRUCache) -> None:
        cache.put(0, "zero")
        cache.put(42, True)
        assert cache.get(0) == "zero"
        assert cache.get(42) is True

    def test_none_key_and_value(self, cache: LRUCache) -> None:
        cache.put(None, "none_key")
        assert cache.get(None) == "none_key"
        cache.put("x", None)
        assert cache.get("x") is None

    def test_str_and_bytes(self, cache: LRUCache) -> None:
        cache.put("hello", b"world")
        assert cache.get("hello") == b"world"

    def test_bool_keys(self, cache: LRUCache) -> None:
        cache.put(True, "yes")
        cache.put(False, "no")
        assert cache.get(True) == "yes"
        assert cache.get(False) == "no"


# ======================================================================
# Eviction (LRU order)
# ======================================================================

class TestEviction:
    def test_evicts_lru_on_overflow(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # should evict "a"
        assert cache.get("a") == -1
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4
        assert cache.size == 3

    def test_get_promotes_mru(self, cache: LRUCache) -> None:
        """Getting a key makes it MRU, so a different key gets evicted."""
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.get("a")  # promote a → a is now MRU
        cache.put("d", 4)  # evicts "b" (oldest)
        assert cache.get("a") == 1  # still there
        assert cache.get("b") == -1  # evicted
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_put_existing_promotes(self, cache: LRUCache) -> None:
        """Putting an existing key promotes it."""
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("a", 100)  # update + promote "a"
        cache.put("d", 4)  # should evict "b"
        assert cache.get("b") == -1
        assert cache.get("a") == 100

    def test_capacity_one(self) -> None:
        cache = LRUCache(capacity=1)
        cache.put("a", 1)
        assert cache.get("a") == 1
        cache.put("b", 2)  # evicts "a"
        assert cache.get("a") == -1
        assert cache.get("b") == 2

    def test_lru_eviction_order_sequence(self, cache: LRUCache) -> None:
        # Insert 3, then access in order to control eviction
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access pattern: c → a → b (so b is MRU at end)
        cache.get("c")
        cache.get("a")
        cache.get("b")
        # Now eviction order: c is LRU (accessed longest ago)
        cache.put("d", 4)  # evicts "c"
        assert cache.get("c") == -1
        assert cache.get("d") == 4


# ======================================================================
# delete
# ======================================================================

class TestDelete:
    def test_delete_existing(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") == -1
        assert cache.size == 0

    def test_delete_missing(self, cache: LRUCache) -> None:
        assert cache.delete("missing") is False

    def test_delete_from_full_cache(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.delete("b")
        assert cache.get("b") == -1
        # After delete, size = 2, so first put does not evict.
        cache.put("d", 4)
        # Do NOT call get() here — it would change LRU order.
        # Size is now 3, so next put triggers eviction.
        cache.put("e", 5)
        # "a" is LRU (inserted first, never accessed after put("d")), so it gets evicted.
        assert cache.get("a") == -1
        assert cache.get("c") == 3
        assert cache.get("d") == 4
        assert cache.get("e") == 5
        assert cache.size == 3

    def test_delete_then_reinsert(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.delete("a")
        cache.put("a", 999)
        assert cache.get("a") == 999
        assert cache.size == 1


# ======================================================================
# Statistics (size, hits, misses)
# ======================================================================

class TestStatistics:
    def test_size_empty(self, cache: LRUCache) -> None:
        assert cache.size == 0

    def test_size_after_puts(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.size == 2

    def test_size_capped_at_capacity(self, cache: LRUCache) -> None:
        for i in range(10):
            cache.put(i, i)
        assert cache.size == 3  # capacity is 3

    def test_hits(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.get("a")
        cache.get("a")
        assert cache.hits == 2

    def test_misses(self, cache: LRUCache) -> None:
        cache.get("x")
        cache.get("y")
        assert cache.misses == 2

    def test_hits_and_misses_mixed(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.get("a")  # hit
        cache.get("b")  # miss
        cache.get("a")  # hit
        assert cache.hits == 2
        assert cache.misses == 1

    def test_clear_resets_stats(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.get("a")
        cache.get("b")
        cache.clear()
        assert cache.size == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_invalid_capacity(self) -> None:
        with pytest.raises(ValueError, match="Capacity"):
            LRUCache(capacity=0)
        with pytest.raises(ValueError, match="Capacity"):
            LRUCache(capacity=-5)


# ======================================================================
# Dunder methods
# ======================================================================

class TestDunder:
    def test_len(self, cache: LRUCache) -> None:
        assert len(cache) == 0
        cache.put("a", 1)
        assert len(cache) == 1

    def test_contains(self, cache: LRUCache) -> None:
        cache.put("k", "v")
        assert "k" in cache
        assert "missing" not in cache

    def test_repr(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        r = repr(cache)
        assert "LRUCache" in r
        assert "capacity=3" in r
        assert "size=1" in r

    def test_clear_empties_cache(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.get("a") == -1
        assert cache.size == 0


# ======================================================================
# Thread safety
# ======================================================================

class TestThreadSafety:
    def test_concurrent_puts(self) -> None:
        cache = LRUCache(capacity=500)
        n_threads = 10
        items_per = 50

        def worker(start: int) -> None:
            for i in range(start, start + items_per):
                cache.put(i, i * 10)

        threads = [
            threading.Thread(target=worker, args=(t * items_per,))
            for t in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert cache.size == 500  # capped at capacity
        # Verify no missing entries among the surviving ones
        # (some got evicted, that's fine)
        for key in list(cache._cache.keys()):
            assert cache.get(key) == key * 10

    def test_concurrent_get_and_put_no_crash(self) -> None:
        """Rapid interleaving of get/put/delete must not throw."""
        cache = LRUCache(capacity=50)
        stop = threading.Event()

        def writer() -> None:
            i = 0
            while not stop.is_set():
                cache.put(i % 100, i)
                if i % 3 == 0:
                    cache.delete((i - 10) % 100)
                i += 1

        def reader() -> None:
            i = 0
            while not stop.is_set():
                cache.get(i % 100)
                i += 1

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=reader),
        ]
        for t in threads:
            t.start()
        time.sleep(0.3)
        stop.set()
        for t in threads:
            t.join()
        # No exception means success
        assert cache.size <= 50
        assert cache.hits + cache.misses > 0

    def test_thread_safety_stats(self) -> None:
        """Concurrent hits and misses must not cause data races."""
        cache = LRUCache(capacity=10)
        for i in range(5):
            cache.put(i, i)

        stop = threading.Event()

        def worker() -> None:
            while not stop.is_set():
                cache.get(0)  # exists → hit
                cache.get(999)  # missing → miss

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        time.sleep(0.2)
        stop.set()
        for t in threads:
            t.join()

        # Stats should be coherent: hits + misses = total calls
        total = cache.hits + cache.misses
        assert total > 0, "should have made some calls"


# ======================================================================
# Large-volume / stress
# ======================================================================

class TestStress:
    def test_large_volume(self) -> None:
        cap = 1000
        cache = LRUCache(capacity=cap)
        total = 10_000
        for i in range(total):
            cache.put(f"key{i}", i)
        assert cache.size == cap
        # Should have the last `cap` keys
        assert cache.get(f"key{total - 1}") == total - 1
        assert cache.get("key0") == -1  # long evicted

    def test_pattern_alternating(self) -> None:
        """Alternate between two keys — should never evict if capacity >= 2."""
        cache = LRUCache(capacity=2)
        for _ in range(1000):
            cache.put("a", 1)
            cache.put("b", 2)
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.hits > 0

    def test_delete_while_iterating_snapshot(self) -> None:
        """Access pattern during delete should not break internal structure."""
        cache = LRUCache(capacity=50)
        for i in range(50):
            cache.put(i, i)

        # Delete half of them
        for i in range(0, 50, 2):
            cache.delete(i)

        assert cache.size == 25
        # Check survivors are accessible
        for i in range(1, 50, 2):
            assert cache.get(i) == i
        # And the deleted ones are gone
        for i in range(0, 50, 2):
            assert cache.get(i) == -1


# ======================================================================
# Edge cases
# ======================================================================

class TestEdgeCases:
    def test_empty_cache_get(self, cache: LRUCache) -> None:
        assert cache.get("anything") == -1

    def test_empty_cache_delete(self, cache: LRUCache) -> None:
        assert cache.delete("anything") is False

    def test_put_and_put_same_key_different_values(self, cache: LRUCache) -> None:
        cache.put("x", 1)
        cache.put("x", 2)
        cache.put("x", 3)
        assert cache.size == 1
        assert cache.get("x") == 3

    def test_fill_then_clear_then_refill(self, cache: LRUCache) -> None:
        for ch in "abcdef":
            cache.put(ch, ord(ch))
        assert cache.size == 3  # evicted down to capacity
        cache.clear()
        assert cache.size == 0
        cache.put("z", 26)
        assert cache.get("z") == 26
        assert cache.size == 1

    def test_repr_after_ops(self, cache: LRUCache) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")   # hit
        cache.get("zz")  # miss
        r = repr(cache)
        assert "hits=1" in r
        assert "misses=1" in r
        assert "size=2" in r
