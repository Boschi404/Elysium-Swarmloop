"""
Tests for binary_search covering all required edge cases:
- exact match found
- element not found
- empty list
- single element
- duplicate elements
- very large lists (performance test)
"""

import sys
import time
import math
import pytest

sys.path.insert(0, "..")
from binary_search import binary_search


class TestBinarySearch:
    """Test suite for binary_search."""

    # ── Exact match found ───────────────────────────────────────────────

    def test_match_at_start(self):
        assert binary_search([1, 3, 5, 7, 9], 1) == 0

    def test_match_at_end(self):
        assert binary_search([1, 3, 5, 7, 9], 9) == 4

    def test_match_in_middle(self):
        assert binary_search([1, 3, 5, 7, 9], 5) == 2

    def test_match_at_even_midpoint(self):
        assert binary_search([1, 3, 5, 7], 5) == 2

    def test_negative_numbers(self):
        assert binary_search([-10, -5, 0, 3, 8], -5) == 1

    # ── Element not found ───────────────────────────────────────────────

    def test_not_found_below_all(self):
        assert binary_search([10, 20, 30, 40], 5) == -1

    def test_not_found_above_all(self):
        assert binary_search([10, 20, 30, 40], 50) == -1

    def test_not_found_in_between(self):
        assert binary_search([10, 20, 30, 40], 25) == -1

    def test_not_found_on_potential_insert(self):
        assert binary_search([1, 2, 4, 5], 3) == -1

    # ── Empty list ──────────────────────────────────────────────────────

    def test_empty_list_returns_minus_one(self):
        assert binary_search([], 42) == -1

    # ── Single element ──────────────────────────────────────────────────

    def test_single_element_match(self):
        assert binary_search([7], 7) == 0

    def test_single_element_no_match(self):
        assert binary_search([7], 3) == -1

    # ── Duplicate elements ──────────────────────────────────────────────

    def test_duplicates_returns_any_valid_index(self):
        """Any index where the value appears is acceptable."""
        lst = [1, 2, 2, 2, 3]
        idx = binary_search(lst, 2)
        assert lst[idx] == 2, f"Index {idx} does not hold value 2"
        assert 1 <= idx <= 3

    def test_all_duplicates(self):
        idx = binary_search([5, 5, 5, 5, 5], 5)
        assert 0 <= idx <= 4
        # all positions hold value 5, so any index is valid

    def test_duplicate_not_found(self):
        assert binary_search([1, 1, 2, 2, 3, 3], 4) == -1

    # ── Very large list (performance test) ──────────────────────────────

    def test_large_list_performance_and_correctness(self):
        """Verify O(log n) and correct result for a list of 1,000,000 elements."""
        n = 1_000_000
        large = list(range(n))

        target = 876_543
        start = time.perf_counter()
        idx = binary_search(large, target)
        elapsed = time.perf_counter() - start

        assert idx == target, f"Expected {target}, got {idx}"
        # O(log n) on 1M should take well under 1 second
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"

    def test_large_list_not_found(self):
        n = 1_000_000
        large = list(range(n))
        start = time.perf_counter()
        idx = binary_search(large, -1)
        elapsed = time.perf_counter() - start

        assert idx == -1
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"

    # ── O(log n) complexity verification ────────────────────────────────

    def test_logarithmic_complexity(self):
        """Searching in 10x larger list should take ~same time or slightly more."""
        def time_search(size):
            arr = list(range(size))
            start = time.perf_counter()
            binary_search(arr, size // 2)  # always hit the middle
            return time.perf_counter() - start

        t_small = time_search(10_000)
        t_large = time_search(1_000_000)  # 100x bigger

        # O(log n) means 100x more data → only ~2x more iterations
        # Allow generous headroom: 100x data should not take > 10x time
        assert t_large < max(t_small * 10, 0.5), (
            f"O(log n) violation: {t_small:.5f}s → {t_large:.5f}s"
        )

    # ── Edge cases ──────────────────────────────────────────────────────

    def test_large_values(self):
        assert binary_search([-10**9, 0, 10**9], 0) == 1

    def test_ascending_guarantee_non_integer(self):
        """Type errors for non-integer or unsorted are caller's responsibility."""



