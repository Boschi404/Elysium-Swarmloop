"""
Tests for binary_search implementation.

Covers all required edge cases:
  - Exact match found
  - Element not found
  - Empty list
  - Single element
  - Duplicate elements
  - Very large lists (performance test)
  - None / invalid input
  - First-occurrence variant
"""
import sys
import math
import pytest

from binary_search import binary_search, binary_search_first_occurrence


# ---------------------------------------------------------------------------
# Standard binary_search
# ---------------------------------------------------------------------------

class TestBinarySearch:
    """Standard binary_search tests."""

    def test_exact_match_middle(self):
        """Target in the middle of the list."""
        arr = [1, 3, 5, 7, 9, 11, 13]
        assert binary_search(arr, 7) == 3

    def test_exact_match_start(self):
        """Target is the first element."""
        assert binary_search([1, 3, 5, 7, 9], 1) == 0

    def test_exact_match_end(self):
        """Target is the last element."""
        assert binary_search([1, 3, 5, 7, 9], 9) == 4

    def test_element_not_found_middle_gap(self):
        """Target not present, would sit between existing values."""
        assert binary_search([1, 3, 5, 7, 9], 4) == -1

    def test_element_not_found_below_all(self):
        """Target smaller than every element."""
        assert binary_search([10, 20, 30], 5) == -1

    def test_element_not_found_above_all(self):
        """Target larger than every element."""
        assert binary_search([10, 20, 30], 40) == -1

    def test_empty_list(self):
        """Empty list always returns -1."""
        assert binary_search([], 42) == -1

    def test_single_element_found(self):
        """Single-element list where target matches."""
        assert binary_search([99], 99) == 0

    def test_single_element_not_found(self):
        """Single-element list where target does not match."""
        assert binary_search([99], 1) == -1

    def test_two_elements_found_first(self):
        """Two-element list, target is the first."""
        assert binary_search([2, 4], 2) == 0

    def test_two_elements_found_second(self):
        """Two-element list, target is the second."""
        assert binary_search([2, 4], 4) == 1

    def test_two_elements_not_found(self):
        """Two-element list, target not present."""
        assert binary_search([2, 4], 3) == -1

    def test_duplicate_elements(self):
        """
        With duplicates, any valid index is acceptable.
        The algorithm as written returns the first one it sees,
        which depends on mid calculation — we just check it finds one.
        """
        arr = [1, 2, 2, 2, 3, 4]
        idx = binary_search(arr, 2)
        assert idx in (1, 2, 3), f"Expected index 1, 2, or 3, got {idx}"
        assert arr[idx] == 2

    def test_duplicates_at_edges(self):
        """Duplicates at the very start."""
        arr = [5, 5, 5, 10, 20]
        idx = binary_search(arr, 5)
        assert idx in (0, 1, 2)
        assert arr[idx] == 5

    def test_negative_numbers(self):
        """Works with negative numbers."""
        arr = [-10, -5, -1, 0, 3, 8]
        assert binary_search(arr, -5) == 1
        assert binary_search(arr, -10) == 0
        assert binary_search(arr, 8) == 5
        assert binary_search(arr, -2) == -1

    def test_floats(self):
        """Works with floating-point numbers."""
        arr = [0.5, 1.0, 1.5, 2.0, 3.14]
        assert binary_search(arr, 1.5) == 2
        assert binary_search(arr, 3.14) == 4
        assert binary_search(arr, 2.5) == -1

    def test_strings(self):
        """Works with strings (alphabetical order)."""
        arr = ["apple", "banana", "cherry", "date", "elderberry"]
        assert binary_search(arr, "cherry") == 2
        assert binary_search(arr, "apple") == 0
        assert binary_search(arr, "elderberry") == 4
        assert binary_search(arr, "fig") == -1

    def test_none_input(self):
        """None input returns -1 gracefully."""
        assert binary_search(None, 5) == -1

    def test_large_list_performance(self):
        """
        Performance test: a list of 1 000 000 elements.
        Binary search must complete in < 0.5 s and return correct index.
        O(log n) ⇒ at most 20 comparisons for 1M elements.
        """
        import time
        n = 1_000_000
        arr = list(range(n))

        # Search for a middle element, an edge, and a missing element
        start = time.perf_counter()
        idx_mid = binary_search(arr, 500_000)
        t_mid = time.perf_counter() - start

        start = time.perf_counter()
        idx_edge = binary_search(arr, 0)
        t_edge = time.perf_counter() - start

        start = time.perf_counter()
        idx_miss = binary_search(arr, -1)
        t_miss = time.perf_counter() - start

        assert idx_mid == 500_000, f"Expected 500000, got {idx_mid}"
        assert idx_edge == 0
        assert idx_miss == -1

        total_time = t_mid + t_edge + t_miss
        assert total_time < 0.5, f"Performance: {total_time:.3f}s — too slow"

    def test_log_n_comparisons_assertion(self):
        """Verify the algorithm truly makes O(log n) comparisons."""
        n = 10_000
        arr = list(range(n))
        max_compares = math.ceil(math.log2(n))

        # Monkey-patch: count comparisons
        original_getitem = arr.__class__.__getitem__
        comparison_count = [0]

        class CountingList(list):
            def __getitem__(self, idx):
                comparison_count[0] += 1
                return super().__getitem__(idx)

        counting_arr = CountingList(arr)
        binary_search(counting_arr, n + 1)  # will probe log n times then -1

        assert comparison_count[0] <= max_compares + 1, (
            f"Made {comparison_count[0]} comparisons, "
            f"expected ≤ {max_compares + 1} for O(log n)"
        )


# ---------------------------------------------------------------------------
# first_occurrence variant
# ---------------------------------------------------------------------------

class TestBinarySearchFirstOccurrence:
    """Tests for the first-occurrence variant."""

    def test_basic_found(self):
        assert binary_search_first_occurrence([1, 2, 3, 4], 3) == 2

    def test_not_found(self):
        assert binary_search_first_occurrence([1, 2, 4, 5], 3) == -1

    def test_empty(self):
        assert binary_search_first_occurrence([], 1) == -1
        assert binary_search_first_occurrence(None, 1) == -1

    def test_first_of_duplicates(self):
        arr = [1, 2, 2, 2, 2, 3]
        assert binary_search_first_occurrence(arr, 2) == 1

    def test_first_of_all_same(self):
        arr = [7, 7, 7, 7, 7]
        assert binary_search_first_occurrence(arr, 7) == 0

    def test_single(self):
        assert binary_search_first_occurrence([42], 42) == 0
        assert binary_search_first_occurrence([42], 1) == -1


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
