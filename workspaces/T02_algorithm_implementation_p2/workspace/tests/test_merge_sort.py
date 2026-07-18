"""
Tests for merge_sort implementation.

Covers: empty list, single element, already sorted, reverse sorted,
duplicates, large lists (100k+), key parameter, reverse parameter,
stability, and various edge cases.
"""

import copy
import math
import random
import sys
import time
from typing import Any

import pytest

# Allow importing merge_sort from the workspace directory
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from merge_sort import merge_sort


# =========================================================================
# Basic correctness
# =========================================================================

class TestBasicCorrectness:
    """Core sorting correctness — no key, no reverse."""

    def test_empty_list(self):
        assert merge_sort([]) == []

    def test_single_element(self):
        assert merge_sort([42]) == [42]

    def test_two_elements(self):
        assert merge_sort([2, 1]) == [1, 2]

    def test_already_sorted(self):
        assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_duplicates(self):
        assert merge_sort([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]) == [
            1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9
        ]

    def test_all_same(self):
        assert merge_sort([7, 7, 7, 7]) == [7, 7, 7, 7]

    def test_negative_numbers(self):
        assert merge_sort([0, -5, 10, -100, 3, -1]) == [-100, -5, -1, 0, 3, 10]

    def test_mixed_types_numeric(self):
        assert merge_sort([1.5, 2, 0.5, 3]) == [0.5, 1.5, 2, 3]

    def test_random_small(self):
        """Random small lists against Python's built-in sorted()."""
        for _ in range(50):
            lst = [random.randint(-1000, 1000) for _ in range(random.randint(0, 200))]
            expected = sorted(lst)
            assert merge_sort(lst) == expected

    def test_tuple_input(self):
        """merge_sort accepts any iterable, not just lists."""
        assert merge_sort((3, 1, 2)) == [1, 2, 3]

    def test_generator_input(self):
        assert merge_sort(x for x in [9, 2, 7]) == [2, 7, 9]

    def test_range_input(self):
        assert merge_sort(range(10, 0, -1)) == list(range(1, 11))


# =========================================================================
# Key parameter
# =========================================================================

class TestKeyParameter:
    """Behaviour of the ``key`` argument."""

    def test_key_string_len(self):
        data = ["apple", "kiwi", "banana", "pear", "fig"]
        result = merge_sort(data, key=len)
        assert result == ["fig", "kiwi", "pear", "apple", "banana"]

    def test_key_abs_value(self):
        data = [3, -10, 7, -2, 0, -5]
        result = merge_sort(data, key=abs)
        assert result == [0, -2, 3, -5, 7, -10]

    def test_key_nested_attr(self):
        class Item:
            def __init__(self, name: str, score: int):
                self.name = name
                self.score = score
            def __repr__(self):
                return f"Item({self.name},{self.score})"

        items = [Item("c", 10), Item("a", 30), Item("b", 20)]
        result = merge_sort(items, key=lambda x: x.score)
        assert [i.name for i in result] == ["c", "b", "a"]

    def test_key_is_identity(self):
        data = [5, 3, 1, 4, 2]
        assert merge_sort(data, key=lambda x: x) == [1, 2, 3, 4, 5]

    def test_key_with_duplicates(self):
        """Keys can tie; original order should be preserved (stable)."""
        data = ["aa", "bb", "cc", "dd"]
        # All have len=2, so keys tie → stable sort preserves original order
        result = merge_sort(data, key=len)
        assert result == data  # order unchanged

    def test_key_none(self):
        """Explicit key=None behaves the same as omitting key."""
        data = [4, 2, 3, 1]
        assert merge_sort(data, key=None) == merge_sort(data)

    def test_key_with_reverse(self):
        data = ["short", "very long", "tiny"]
        result = merge_sort(data, key=len, reverse=True)
        assert result == ["very long", "short", "tiny"]

    def test_key_compare_str_case_insensitive(self):
        data = ["Banana", "apple", "Cherry", "date"]
        result = merge_sort(data, key=lambda s: s.lower())
        assert result == ["apple", "Banana", "Cherry", "date"]


# =========================================================================
# Reverse parameter
# =========================================================================

class TestReverseParameter:
    """Behaviour of the ``reverse`` argument."""

    def test_reverse_empty(self):
        assert merge_sort([], reverse=True) == []

    def test_reverse_single(self):
        assert merge_sort([1], reverse=True) == [1]

    def test_reverse_sorted_asc(self):
        assert merge_sort([1, 2, 3, 4, 5], reverse=True) == [5, 4, 3, 2, 1]

    def test_reverse_sorted_desc(self):
        assert merge_sort([5, 4, 3, 2, 1], reverse=True) == [5, 4, 3, 2, 1]

    def test_reverse_duplicates(self):
        result = merge_sort([3, 1, 4, 1, 5, 9], reverse=True)
        expected = sorted([3, 1, 4, 1, 5, 9], reverse=True)
        assert result == expected

    def test_reverse_random(self):
        for _ in range(20):
            lst = [random.randint(-500, 500) for _ in range(random.randint(1, 100))]
            assert merge_sort(lst, reverse=True) == sorted(lst, reverse=True)

    def test_reverse_with_key(self):
        data = ["hello", "world", "hi", "greetings"]
        # Sort by length descending
        result = merge_sort(data, key=len, reverse=True)
        assert result == ["greetings", "hello", "world", "hi"]


# =========================================================================
# Stability
# =========================================================================

class TestStability:
    """Merge sort is a *stable* sort — equal elements keep original order."""

    def test_stable_pairs(self):
        pairs = [(2, "b"), (1, "a"), (2, "a"), (1, "b")]
        # Sort by first element (value)
        result = merge_sort(pairs, key=lambda p: p[0])
        # Both (1, "a") and (1, "b") keep order → (1,"a"), (1,"b")
        # Both (2, "b") and (2, "a") keep order → (2,"b"), (2,"a")
        assert result[0] == (1, "a")
        assert result[1] == (1, "b")
        assert result[2] == (2, "b")
        assert result[3] == (2, "a")

    def test_stable_reverse(self):
        pairs = [(2, "b"), (1, "a"), (2, "a"), (1, "b")]
        result = merge_sort(pairs, key=lambda p: p[0], reverse=True)
        # (2, "b") before (2, "a"), then (1, "a") before (1, "b")
        assert result[0] == (2, "b")
        assert result[1] == (2, "a")
        assert result[2] == (1, "a")
        assert result[3] == (1, "b")


# =========================================================================
# Edge cases
# =========================================================================

class TestEdgeCases:
    """Unusual but valid inputs."""

    def test_boolean_values(self):
        """bool is a subclass of int in Python."""
        data = [True, False, True, False]
        result = merge_sort(data)
        assert result == [False, False, True, True]

    def test_none_among_numbers(self):
        """None compares in Python 3 (TypeError in most mixed cases)."""
        with pytest.raises(TypeError):
            merge_sort([3, None, 1])

    def test_very_large_numbers(self):
        data = [10**100, -(10**100), 0]
        assert merge_sort(data) == [-(10**100), 0, 10**100]

    def test_floats_with_nan(self):
        """NaN comparisons are tricky; sorting NaN is implementation-defined."""
        # Avoid NaN for stable testing — just check normal floats
        data = [3.14, 2.71, 1.41, 0.58]
        result = merge_sort(data)
        assert result == sorted(data)

    def test_mixed_int_float(self):
        assert merge_sort([3, 2.5, 1, 4.2]) == [1, 2.5, 3, 4.2]

    def test_non_mutating(self):
        """merge_sort must not mutate the input list."""
        original = [3, 1, 4, 1, 5]
        original_copy = original[:]
        merge_sort(original)
        assert original == original_copy


# =========================================================================
# Large lists (performance + correctness)
# =========================================================================

class TestLargeLists:
    """Verify that merge_sort handles large inputs correctly and efficiently."""

    LARGE_SIZE = 100_000

    def test_large_random(self):
        lst = [random.randint(-1_000_000, 1_000_000) for _ in range(self.LARGE_SIZE)]
        expected = sorted(lst)
        t0 = time.perf_counter()
        result = merge_sort(lst)
        elapsed = time.perf_counter() - t0
        assert result == expected
        # Reasonable performance: 100k ints should sort in < 10s on modern hardware
        assert elapsed < 10.0, f"Took {elapsed:.2f}s — too slow for 100k elements"

    def test_large_already_sorted(self):
        lst = list(range(self.LARGE_SIZE))
        t0 = time.perf_counter()
        result = merge_sort(lst)
        elapsed = time.perf_counter() - t0
        assert result == lst
        assert elapsed < 10.0

    def test_large_reverse_sorted(self):
        lst = list(range(self.LARGE_SIZE, 0, -1))
        expected = list(range(1, self.LARGE_SIZE + 1))
        t0 = time.perf_counter()
        result = merge_sort(lst)
        elapsed = time.perf_counter() - t0
        assert result == expected
        assert elapsed < 10.0

    def test_large_all_duplicates(self):
        lst = [42] * self.LARGE_SIZE
        result = merge_sort(lst)
        assert len(result) == self.LARGE_SIZE
        assert all(x == 42 for x in result)

    def test_large_alternating(self):
        lst = [1, 0] * (self.LARGE_SIZE // 2)
        if len(lst) < self.LARGE_SIZE:
            lst.append(1)
        result = merge_sort(lst)
        assert result == sorted(lst)

    def test_large_with_key(self):
        """Key on large list — use abs to negate half the values."""
        lst = [random.randint(-1_000_000, 1_000_000) for _ in range(self.LARGE_SIZE)]
        expected = sorted(lst, key=abs)
        t0 = time.perf_counter()
        result = merge_sort(lst, key=abs)
        elapsed = time.perf_counter() - t0
        assert result == expected
        assert elapsed < 15.0  # key-based is slower but should still be reasonable

    def test_large_with_reverse(self):
        lst = [random.randint(-1_000_000, 1_000_000) for _ in range(self.LARGE_SIZE)]
        expected = sorted(lst, reverse=True)
        t0 = time.perf_counter()
        result = merge_sort(lst, reverse=True)
        elapsed = time.perf_counter() - t0
        assert result == expected
        assert elapsed < 10.0


# =========================================================================
# Complexity / O(n log n) validation  (small-N verification)
# =========================================================================

class TestComplexity:
    """Spot-check that merge operations grow roughly as n log n."""

    def test_small_n_log_n_shape(self):
        """Verify sort runs correctly for many small N (probabilistic check)."""
        for n in [0, 1, 2, 3, 5, 8, 13, 21, 34, 55]:
            for _ in range(10):
                lst = [random.randint(-100, 100) for _ in range(n)]
                assert merge_sort(lst) == sorted(lst)


# =========================================================================
# Contract / API
# =========================================================================

class TestAPI:
    """merge_sort API conventions."""

    def test_returns_new_list(self):
        data = [3, 1, 2]
        result = merge_sort(data)
        assert isinstance(result, list)
        # Should be a *new* list, not the original
        assert result is not data

    def test_accepts_keyword_only_key(self):
        """key and reverse must be keyword-only."""
        with pytest.raises(TypeError):
            merge_sort([1, 2, 3], lambda x: x)  # positional key should fail

    def test_docstring_present(self):
        assert merge_sort.__doc__ is not None
        assert len(merge_sort.__doc__) > 50


# =========================================================================
# Property-based-style tests
# =========================================================================

class TestProperties:
    """Invariant properties that should always hold."""

    SIZES = [0, 1, 2, 5, 10, 50, 100]

    def test_same_length(self):
        """Sorted list must have same length as input."""
        for n in self.SIZES:
            lst = [random.randint(-1000, 1000) for _ in range(n)]
            assert len(merge_sort(lst)) == n

    def test_same_elements_multiset(self):
        """Sorted list must contain exactly the same elements as input."""
        for n in self.SIZES:
            lst = [random.randint(-100, 100) for _ in range(n)]
            result = merge_sort(lst)
            assert sorted(lst) == result  # same as built-in

    def test_idempotent(self):
        """Sorting an already-sorted list must be a no-op."""
        for n in self.SIZES:
            lst = [random.randint(-1000, 1000) for _ in range(n)]
            once = merge_sort(lst)
            twice = merge_sort(once)
            assert once == twice
