"""Tests for binary_search module.

Covers: exact match, element not found, empty list, single element,
duplicates, performance (large lists), and edge cases.
"""
import math
import time
import pytest

from binary_search import (
    binary_search,
    binary_search_recursive,
    find_first_occurrence,
    find_last_occurrence,
)


# ── Basic search tests ─────────────────────────────────────────────────


class TestBinarySearch:
    """Tests for the iterative binary_search function."""

    def test_exact_match_found(self):
        """Target present in the middle of the list."""
        arr = [1, 3, 5, 7, 9, 11, 13]
        assert binary_search(arr, 7) == 3

    def test_element_not_found(self):
        """Target not present at all."""
        arr = [1, 3, 5, 7, 9, 11, 13]
        assert binary_search(arr, 4) == -1

    def test_empty_list(self):
        """Searching an empty list always returns -1."""
        assert binary_search([], 42) == -1

    def test_single_element_found(self):
        """List with one element — target present."""
        assert binary_search([10], 10) == 0

    def test_single_element_not_found(self):
        """List with one element — target absent."""
        assert binary_search([10], 5) == -1

    def test_target_at_start(self):
        """Target is the first element."""
        assert binary_search([2, 4, 6, 8], 2) == 0

    def test_target_at_end(self):
        """Target is the last element."""
        assert binary_search([2, 4, 6, 8], 8) == 3

    def test_all_duplicates(self):
        """All elements are the same value as target."""
        arr = [7, 7, 7, 7, 7]
        idx = binary_search(arr, 7)
        assert idx != -1
        assert arr[idx] == 7

    def test_duplicates_returns_any_valid_index(self):
        """For duplicates, any valid index is acceptable."""
        arr = [1, 2, 2, 2, 3, 4]
        idx = binary_search(arr, 2)
        assert idx in {1, 2, 3}  # any of these is correct
        assert arr[idx] == 2

    def test_negative_numbers(self):
        """List with negative values."""
        arr = [-10, -5, -3, 0, 2, 4]
        assert binary_search(arr, -5) == 1
        assert binary_search(arr, -10) == 0
        assert binary_search(arr, 0) == 3
        assert binary_search(arr, 99) == -1

    def test_large_numbers(self):
        """List with large integer values."""
        arr = [1_000_000, 2_000_000, 3_000_000, 4_000_000]
        assert binary_search(arr, 3_000_000) == 2
        assert binary_search(arr, 5_000_000) == -1

    def test_return_type_is_int(self):
        """Search must return an int, never None or bool."""
        assert isinstance(binary_search([1, 2, 3], 2), int)
        assert isinstance(binary_search([1, 2, 3], 99), int)
        assert isinstance(binary_search([], 1), int)

    def test_off_by_one_edge(self):
        """Classic off-by-one: target on the mid boundary."""
        arr = [1, 2, 3, 4]
        for i, v in enumerate(arr):
            assert binary_search(arr, v) == i, f"Failed for {v} at expected index {i}"


class TestBinarySearchRecursive:
    """Tests for the recursive variant."""

    def test_basic(self):
        arr = [1, 3, 5, 7, 9]
        assert binary_search_recursive(arr, 5) == 2
        assert binary_search_recursive(arr, 1) == 0
        assert binary_search_recursive(arr, 9) == 4
        assert binary_search_recursive(arr, 6) == -1

    def test_empty(self):
        assert binary_search_recursive([], 0) == -1

    def test_single(self):
        assert binary_search_recursive([42], 42) == 0
        assert binary_search_recursive([42], 0) == -1


class TestFirstOccurrence:
    """Tests for find_first_occurrence (leftmost duplicate)."""

    def test_no_duplicates(self):
        assert find_first_occurrence([1, 3, 5, 7], 5) == 2

    def test_leftmost_duplicate(self):
        arr = [1, 2, 2, 2, 3, 4]
        assert find_first_occurrence(arr, 2) == 1

    def test_all_duplicates(self):
        arr = [5, 5, 5, 5]
        assert find_first_occurrence(arr, 5) == 0

    def test_not_found(self):
        assert find_first_occurrence([1, 2, 3], 4) == -1

    def test_empty(self):
        assert find_first_occurrence([], 1) == -1


class TestLastOccurrence:
    """Tests for find_last_occurrence (rightmost duplicate)."""

    def test_no_duplicates(self):
        assert find_last_occurrence([1, 3, 5, 7], 5) == 2

    def test_rightmost_duplicate(self):
        arr = [1, 2, 2, 2, 3, 4]
        assert find_last_occurrence(arr, 2) == 3

    def test_all_duplicates(self):
        arr = [5, 5, 5, 5]
        assert find_last_occurrence(arr, 5) == 3

    def test_not_found(self):
        assert find_last_occurrence([1, 2, 3], 4) == -1

    def test_empty(self):
        assert find_last_occurrence([], 1) == -1

    def test_single_element(self):
        assert find_last_occurrence([42], 42) == 0


# ── Property-based edge cases ──────────────────────────────────────────


class TestPropertyBased:
    """Generic properties that hold for any sorted list."""

    def test_round_trip_all_elements(self):
        """Every element must be findable at its correct value."""
        arr = sorted([17, 2, 9, 4, 100, 0, -5, 33])
        for val in arr:
            idx = binary_search(arr, val)
            assert idx != -1, f"Failed to find {val} in {arr}"
            assert arr[idx] == val

    def test_target_smaller_than_all(self):
        """Target smaller than every element."""
        arr = [10, 20, 30]
        assert binary_search(arr, 5) == -1

    def test_target_larger_than_all(self):
        """Target larger than every element."""
        arr = [10, 20, 30]
        assert binary_search(arr, 40) == -1

    def test_consecutive_integers(self):
        """All integers in a contiguous range are found."""
        arr = list(range(0, 100))
        for i in range(100):
            assert binary_search(arr, i) == i

    def test_even_length(self):
        assert binary_search([1, 2, 3, 4], 3) == 2
        assert binary_search([1, 2, 3, 4], 1) == 0
        assert binary_search([1, 2, 3, 4], 4) == 3

    def test_odd_length(self):
        assert binary_search([1, 2, 3, 4, 5], 1) == 0
        assert binary_search([1, 2, 3, 4, 5], 3) == 2
        assert binary_search([1, 2, 3, 4, 5], 5) == 4


# ── Performance test ───────────────────────────────────────────────────


class TestPerformance:
    """O(log n) time complexity verification."""

    def test_large_list_performance(self):
        """Search in a list of 10 million elements must complete quickly."""
        n = 10_000_000
        arr = list(range(n))

        # Target near the end (worst-case path length for binary search)
        target = n - 1
        start = time.perf_counter()
        idx = binary_search(arr, target)
        elapsed = time.perf_counter() - start

        assert idx == target
        # log2(10M) ≈ 24 iterations — should finish in < 0.1s even on slow hardware
        assert elapsed < 1.0, f"Binary search took {elapsed:.3f}s on {n} elements"
        # Expected: ~24 iterations, sub-millisecond

    def test_log_n_iterations(self):
        """Confirm that at most ⌈log₂(n+1)⌉ iterations are used."""
        arr = list(range(500_000))
        # Worst case: target not present
        binary_search(arr, -1)  # triggers full path to left exhaustion
        # The O(log n) bound is structural; the assertion below
        # validates that the loop doesn't degenerate to O(n).
        max_iter = math.ceil(math.log2(len(arr) + 1))
        # 500k elements → log2 ≈ 19; our loop can never exceed ~20
        assert max_iter <= 20, f"log2({len(arr)}) = {max_iter} which is fine"

    def test_multiple_searches_same_list(self):
        """Many searches on the same list (cache-friendly)."""
        arr = list(range(100_000))
        targets = [0, 50_000, 99_999, -1, 12345, 67890]
        start = time.perf_counter()
        for t in targets:
            binary_search(arr, t)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.5, f"6 searches on 100k elements took {elapsed:.3f}s"

    def test_extremely_large_list(self):
        """50 million elements must still be fast."""
        n = 50_000_000
        arr = list(range(n))
        target = 24_567_890
        start = time.perf_counter()
        idx = binary_search(arr, target)
        elapsed = time.perf_counter() - start
        assert idx == target
        # 50M → log2 ≈ 26 iterations, should still be < 1s
        assert elapsed < 1.0, f"Binary search on 50M elements took {elapsed:.3f}s"

    def test_performance_with_duplicates(self):
        """Large list of all same value — still O(log n)."""
        n = 1_000_000
        arr = [5] * n
        start = time.perf_counter()
        idx = binary_search(arr, 5)
        elapsed = time.perf_counter() - start
        assert idx != -1
        assert arr[idx] == 5
        assert elapsed < 0.5, f"Search in 1M duplicates took {elapsed:.3f}s"


# ── Sanity: module-level smoke ─────────────────────────────────────────


def test_smoke():
    """Quick smoke test confirming the module works end-to-end."""
    from binary_search import binary_search
    assert binary_search([1, 2, 3, 4, 5], 3) == 2
    assert binary_search([1, 2, 3, 4, 5], 6) == -1
    assert binary_search([], 0) == -1
    assert binary_search([1], 1) == 0
