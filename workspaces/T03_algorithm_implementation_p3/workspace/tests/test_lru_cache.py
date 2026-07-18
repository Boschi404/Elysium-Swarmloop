"""
Comprehensive test suite for LRUCache.

Covers: basic operations, eviction, LRU ordering, thread safety,
edge cases (empty, single item, capacity=1), hit/miss tracking,
error handling, and __contains__/__len__.
"""

from __future__ import annotations

import threading
import time
from typing import Any

import pytest

from lru_cache import LRUCache


# ── Fixtures ─────────────────────────────────────────────────


@pytest.fixture
def cache() -> LRUCache[str, int]:
    return LRUCache[str, int](capacity=3)


@pytest.fixture
def filled_cache(cache: LRUCache[str, int]) -> LRUCache[str, int]:
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    return cache


# ── Construction ──────────────────────────────────────────────


class TestConstruction:
    def test_default_capacity(self) -> None:
        c: LRUCache[str, int] = LRUCache(5)
        assert c.capacity == 5
        assert c.size == 0

    def test_invalid_capacity_zero(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            LRUCache(0)

    def test_invalid_capacity_negative(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            LRUCache(-1)

    def test_type_generic_works(self) -> None:
        c: LRUCache[int, str] = LRUCache[int, str](2)
        c.put(1, "one")
        assert c.get(1) == "one"


# ── get / put — Basic ────────────────────────────────────────


class TestGetPut:
    def test_get_missing(self, cache: LRUCache[str, int]) -> None:
        assert cache.get("nonexistent") == -1

    def test_put_and_get(self, cache: LRUCache[str, int]) -> None:
        cache.put("x", 42)
        assert cache.get("x") == 42

    def test_put_overwrite(self, cache: LRUCache[str, int]) -> None:
        cache.put("k", 1)
        cache.put("k", 99)
        assert cache.get("k") == 99
        assert cache.size == 1

    def test_put_none_value(self, cache: LRUCache[Any, Any]) -> None:
        cache.put("null", None)
        assert cache.get("null") is None

    def test_put_str_key_int_value(self) -> None:
        c: LRUCache[str, int] = LRUCache(2)
        c.put("one", 1)
        assert c.get("one") == 1

    def test_get_preserves_other_entries(
        self, filled_cache: LRUCache[str, int]
    ) -> None:
        assert filled_cache.get("a") == 1
        assert filled_cache.get("b") == 2
        assert filled_cache.get("c") == 3
        assert filled_cache.size == 3


# ── Eviction ─────────────────────────────────────────────────


class TestEviction:
    def test_evicts_lru_after_capacity(self, cache: LRUCache[str, int]) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # should evict "a"
        assert cache.get("a") == -1
        assert cache.get("d") == 4

    def test_eviction_multiple(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Put d and e — first two (a, b) are evicted; c survives
        cache.put("d", 4)
        cache.put("e", 5)
        assert cache.get("a") == -1  # evicted
        assert cache.get("b") == -1  # evicted
        assert cache.get("c") == 3   # 3rd put, still present
        assert cache.get("d") == 4   # present
        assert cache.get("e") == 5   # present
        assert cache.size == 3       # c, d, e

    def test_get_updates_lru_order(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access "a" — makes it most recently used
        cache.get("a")
        # Now "b" is LRU — inserting "d" should evict "b"
        cache.put("d", 4)
        assert cache.get("a") == 1  # still present
        assert cache.get("b") == -1  # evicted
        assert cache.get("c") == 3  # still present
        assert cache.get("d") == 4  # present

    def test_put_updates_lru_order(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Overwrite "a" — makes it most recently used
        cache.put("a", 99)
        # Now "b" is LRU — inserting "d" should evict "b"
        cache.put("d", 4)
        assert cache.get("a") == 99
        assert cache.get("b") == -1
        assert cache.get("d") == 4

    def test_capacity_one(self) -> None:
        c: LRUCache[str, int] = LRUCache(1)
        c.put("a", 1)
        assert c.get("a") == 1
        c.put("b", 2)
        assert c.get("a") == -1
        assert c.get("b") == 2

    def test_no_eviction_under_capacity(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.size == 2
        assert cache.get("a") == 1
        assert cache.get("b") == 2


# ── delete ───────────────────────────────────────────────────


class TestDelete:
    def test_delete_existing(self, filled_cache: LRUCache[str, int]) -> None:
        assert filled_cache.delete("a") is True
        assert filled_cache.get("a") == -1
        assert filled_cache.size == 2

    def test_delete_missing(self, cache: LRUCache[str, int]) -> None:
        assert cache.delete("nonexistent") is False

    def test_delete_middle_then_eviction(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.delete("b")
        cache.put("d", 4)  # should NOT evict "b" (it's gone)
        assert cache.get("b") == -1
        assert cache.get("d") == 4
        assert cache.size == 3

    def test_delete_last_and_refill(
        self, filled_cache: LRUCache[str, int]
    ) -> None:
        filled_cache.delete("c")
        filled_cache.put("d", 4)
        assert filled_cache.get("d") == 4
        assert filled_cache.get("c") == -1
        assert filled_cache.size == 3


# ── Hit / Miss Tracking ──────────────────────────────────────


class TestHitMissTracking:
    def test_initial_counts(self, cache: LRUCache[str, int]) -> None:
        assert cache.hits == 0
        assert cache.misses == 0
        assert cache.hit_rate == 0.0

    def test_miss_increments(self, cache: LRUCache[str, int]) -> None:
        cache.get("x")
        assert cache.misses == 1
        assert cache.hits == 0

    def test_hit_increments(self, filled_cache: LRUCache[str, int]) -> None:
        filled_cache.get("a")
        assert filled_cache.hits == 1
        assert filled_cache.misses == 0

    def test_hit_rate(self, filled_cache: LRUCache[str, int]) -> None:
        filled_cache.get("a")  # hit
        filled_cache.get("x")  # miss
        filled_cache.get("b")  # hit
        filled_cache.get("y")  # miss
        # 2 hits / 4 total = 0.5
        assert filled_cache.hit_rate == 0.5

    def test_hit_rate_no_lookups(self, cache: LRUCache[str, int]) -> None:
        assert cache.hit_rate == 0.0

    def test_put_does_not_affect_hit_miss(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        assert cache.hits == 0
        assert cache.misses == 0

    def test_delete_does_not_affect_hit_miss(
        self, filled_cache: LRUCache[str, int]
    ) -> None:
        filled_cache.delete("a")
        assert filled_cache.hits == 0
        assert filled_cache.misses == 0

    def test_clear_resets_counts(self, filled_cache: LRUCache[str, int]) -> None:
        filled_cache.get("a")  # hit
        filled_cache.get("x")  # miss
        filled_cache.clear()
        assert filled_cache.hits == 0
        assert filled_cache.misses == 0
        assert filled_cache.size == 0


# ── clear ────────────────────────────────────────────────────


class TestClear:
    def test_clear_empties(self, filled_cache: LRUCache[str, int]) -> None:
        filled_cache.clear()
        assert filled_cache.size == 0
        assert filled_cache.get("a") == -1

    def test_clear_then_reuse(self, filled_cache: LRUCache[str, int]) -> None:
        filled_cache.clear()
        filled_cache.put("new", 99)
        assert filled_cache.get("new") == 99
        assert filled_cache.size == 1


# ── Dunder methods ───────────────────────────────────────────


class TestDunder:
    def test_contains(self, filled_cache: LRUCache[str, int]) -> None:
        assert "a" in filled_cache
        assert "z" not in filled_cache

    def test_len(self, cache: LRUCache[str, int]) -> None:
        assert len(cache) == 0
        cache.put("a", 1)
        assert len(cache) == 1

    def test_repr(self, cache: LRUCache[str, int]) -> None:
        r = repr(cache)
        assert "LRUCache" in r
        assert "capacity=3" in r
        assert "size=0" in r

    def test_contains_does_not_update_order(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # "a" __contains__ — should NOT make it MRU
        _ = "a" in cache  # noqa: F841
        cache.put("d", 4)
        # "a" should still be evicted because `in` doesn't affect order
        # Actually, OrderedDict.__contains__ does NOT move to end,
        # but `get` does. Since our __contains__ doesn't call pop,
        # "a" remains LRU and should be evicted.
        assert cache.get("a") == -1


# ── Edge Cases ───────────────────────────────────────────────


class TestEdgeCases:
    def test_large_operations(self) -> None:
        c: LRUCache[int, int] = LRUCache(1000)
        for i in range(1000):
            c.put(i, i * 2)
        assert c.size == 1000
        # All should be retrievable
        for i in range(1000):
            assert c.get(i) == i * 2
        # One more triggers eviction of 0
        c.put(1000, 2000)
        assert c.get(0) == -1
        assert c.get(1000) == 2000

    def test_duplicate_puts_reorder(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("a", 99)  # reorder "a" to MRU
        cache.put("d", 4)
        assert cache.get("b") == -1  # "b" was LRU now
        assert cache.get("a") == 99

    def test_delete_all_then_fill(self, cache: LRUCache[str, int]) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.delete("a")
        cache.delete("b")
        cache.delete("c")
        assert cache.size == 0
        cache.put("d", 4)
        assert cache.get("d") == 4
        assert cache.get("a") == -1

    def test_delete_from_empty_cache(self, cache: LRUCache[str, int]) -> None:
        assert cache.delete("anything") is False


# ── Thread Safety ────────────────────────────────────────────


class TestThreadSafety:
    def test_concurrent_puts(self) -> None:
        """Multiple threads writing simultaneously — no corruption."""
        c: LRUCache[int, int] = LRUCache(100)
        n_threads = 10
        ops_per_thread = 100
        errors: list[Exception] = []

        def worker(start: int) -> None:
            try:
                for i in range(start, start + ops_per_thread):
                    c.put(i, i * 10)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=worker, args=(t * ops_per_thread,))
            for t in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        # Cache should contain up to 100 items (capacity)
        assert c.size <= 100

    def test_concurrent_get_put_no_crash(self) -> None:
        """Read and write from multiple threads — no crash."""
        c: LRUCache[int, int] = LRUCache(50)
        # Pre-fill
        for i in range(50):
            c.put(i, i)

        stop = threading.Event()
        errors: list[Exception] = []

        def writer() -> None:
            try:
                i = 0
                while not stop.is_set():
                    c.put(i, i * 2)
                    i = (i + 1) % 100
            except Exception as e:
                errors.append(e)

        def reader() -> None:
            try:
                while not stop.is_set():
                    c.get(0)
            except Exception as e:
                errors.append(e)

        w = threading.Thread(target=writer)
        r = threading.Thread(target=reader)
        w.start()
        r.start()
        time.sleep(0.5)
        stop.set()
        w.join()
        r.join()

        assert not errors, f"Thread errors: {errors}"
        assert c.hits + c.misses > 0  # some operations ran

    def test_concurrent_delete_put_no_race(
        self, filled_cache: LRUCache[str, int]
    ) -> None:
        """Delete and put on same key — should not corrupt."""
        errors: list[Exception] = []

        def deleter() -> None:
            try:
                for _ in range(50):
                    filled_cache.delete("a")
            except Exception as e:
                errors.append(e)

        def putter() -> None:
            try:
                for _ in range(50):
                    filled_cache.put("a", 999)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=deleter),
            threading.Thread(target=putter),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        # Final state should be consistent (either present or deleted)
        assert filled_cache.size in (2, 3)


# ── Alternative Implementation Compatibility ─────────────────


class TestOrderedDictImplementationSpecifics:
    """These tests validate specific properties of OrderedDict-based impl."""

    def test_put_evicts_lru_correctly(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access "c" to make it MRU
        cache.get("c")
        # Access "a" to make it MRU as well
        cache.get("a")
        # Now "b" should be LRU
        cache.put("d", 4)
        assert cache.get("b") == -1  # evicted
        assert cache.get("a") == 1  # present
        assert cache.get("c") == 3  # present
        assert cache.get("d") == 4  # present

    def test_put_preserves_correct_lru_after_overwrite(
        self, cache: LRUCache[str, int]
    ) -> None:
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Overwrite "a" — moves it to MRU
        cache.put("a", 99)
        # Now "b" is LRU
        cache.put("d", 4)
        assert cache.get("b") == -1  # evicted
        assert cache.get("a") == 99  # present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
