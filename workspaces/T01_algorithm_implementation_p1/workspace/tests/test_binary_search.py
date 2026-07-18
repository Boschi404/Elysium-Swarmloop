"""
Tests for Binary Search Implementation
=======================================
Covers: exact match, element not found, empty list, single element,
        duplicates, edge cases, and large-list performance.
"""

import sys
import os
import time
import math

# Ensure the workspace is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binary_search import binary_search


# --------------------------------------------------------------------------- #
# Basic tests
# --------------------------------------------------------------------------- #
def test_exact_match_found():
    """Target exists in the middle of the list."""
    assert binary_search([1, 2, 3, 4, 5], 3) == 2


def test_exact_match_first_element():
    """Target is the first element."""
    assert binary_search([1, 2, 3, 4, 5], 1) == 0


def test_exact_match_last_element():
    """Target is the last element."""
    assert binary_search([1, 2, 3, 4, 5], 5) == 4


def test_element_not_found():
    """Target is not in the list."""
    assert binary_search([1, 2, 3, 4, 5], 6) == -1


def test_element_not_found_low():
    """Target is smaller than any element."""
    assert binary_search([10, 20, 30], 5) == -1


def test_element_not_found_high():
    """Target is larger than any element."""
    assert binary_search([10, 20, 30], 35) == -1


def test_element_not_found_mid_gap():
    """Target falls between two existing values."""
    assert binary_search([10, 20, 30], 25) == -1


# --------------------------------------------------------------------------- #
# Edge cases
# --------------------------------------------------------------------------- #
def test_empty_list():
    """Empty list returns -1."""
    assert binary_search([], 1) == -1


def test_single_element_found():
    """Single-element list with matching target."""
    assert binary_search([42], 42) == 0


def test_single_element_not_found():
    """Single-element list with non-matching target."""
    assert binary_search([42], 99) == -1


def test_two_elements_found_first():
    """Two-element list, target is first."""
    assert binary_search([1, 2], 1) == 0


def test_two_elements_found_second():
    """Two-element list, target is second."""
    assert binary_search([1, 2], 2) == 1


def test_two_elements_not_found():
    """Two-element list, target missing."""
    assert binary_search([1, 2], 3) == -1


def test_negative_numbers():
    """List with negative numbers."""
    assert binary_search([-10, -5, 0, 5, 10], -5) == 1
    assert binary_search([-10, -5, 0, 5, 10], -10) == 0
    assert binary_search([-10, -5, 0, 5, 10], 10) == 4
    assert binary_search([-10, -5, 0, 5, 10], -7) == -1


def test_all_same_values():
    """List where every element is the same (degenerate)."""
    assert binary_search([7, 7, 7, 7, 7], 7) == 0  # first occurrence
    assert binary_search([7, 7, 7, 7, 7], 8) == -1


# --------------------------------------------------------------------------- #
# Duplicate elements — must return FIRST occurrence
# --------------------------------------------------------------------------- #
def test_duplicates_first_occurrence():
    """Repeated target values — return the leftmost index."""
    assert binary_search([1, 2, 2, 2, 3], 2) == 1


def test_duplicates_at_start():
    """Duplicates at the very beginning of the list."""
    assert binary_search([1, 1, 1, 2, 3], 1) == 0


def test_duplicates_at_end():
    """Duplicates at the very end of the list."""
    assert binary_search([1, 2, 3, 3, 3], 3) == 2


def test_duplicates_single_element_target():
    """Only one copy of the target among other duplicates."""
    assert binary_search([2, 2, 3, 4, 4], 3) == 2


# --------------------------------------------------------------------------- #
# Large list performance test (O(log n) verification)
# --------------------------------------------------------------------------- #
def test_large_list_performance():
    """Binary search on a very large list runs in O(log n) time."""
    n = 10_000_000  # 10 million elements
    large_list = list(range(n))

    target = 9_876_543
    start = time.perf_counter()
    idx = binary_search(large_list, target)
    elapsed = time.perf_counter() - start

    assert idx == target, f"Expected {target}, got {idx}"
    # O(log n) on 10M elements = ~24 comparisons — should complete in < 1s
    assert elapsed < 1.0, f"Binary search took {elapsed:.3f}s (expected < 1s)"


def test_large_list_not_found():
    """Searching for a missing element in a large list is still fast."""
    n = 10_000_000
    large_list = list(range(n))

    start = time.perf_counter()
    idx = binary_search(large_list, -1)  # not present
    elapsed = time.perf_counter() - start

    assert idx == -1
    assert elapsed < 1.0, f"Binary search (not found) took {elapsed:.3f}s"


def test_large_list_first_element():
    """Finding the very first element in a large list."""
    n = 10_000_000
    large_list = list(range(n))

    start = time.perf_counter()
    idx = binary_search(large_list, 0)
    elapsed = time.perf_counter() - start

    assert idx == 0
    assert elapsed < 1.0, f"Binary search (first) took {elapsed:.3f}s"


def test_large_list_last_element():
    """Finding the very last element in a large list."""
    n = 10_000_000
    large_list = list(range(n))

    start = time.perf_counter()
    idx = binary_search(large_list, n - 1)
    elapsed = time.perf_counter() - start

    assert idx == n - 1
    assert elapsed < 1.0, f"Binary search (last) took {elapsed:.3f}s"


def test_log_n_complexity_verification():
    """
    Verify O(log n) by measuring search on increasingly large lists.
    The time should grow logarithmically, not linearly.
    """
    sizes = [1_000, 100_000, 10_000_000]
    times = []

    for n in sizes:
        arr = list(range(n))
        target = n - 1  # worst-case: last element

        start = time.perf_counter()
        binary_search(arr, target)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    # The ratio of times should be roughly log(10M)/log(1k) ≈ 2.3,
    # NOT 10_000 (which would indicate O(n)).
    # Allow generous headroom for system noise.
    if len(times) >= 2:
        ratio = times[-1] / max(times[0], 1e-9)
        assert ratio < 100, (
            f"Time ratio between largest and smallest list is {ratio:.1f}x. "
            f"Expected < 100x for O(log n). Times: {[f'{t:.6f}s' for t in times]}"
        )


# --------------------------------------------------------------------------- #
# Type / contract tests
# --------------------------------------------------------------------------- #
def test_returns_int():
    """Return type is always int."""
    result = binary_search([1, 2, 3], 2)
    assert isinstance(result, int)
    result = binary_search([], 2)
    assert isinstance(result, int)
    result = binary_search([1], 99)
    assert isinstance(result, int)


# --------------------------------------------------------------------------- #
# Run all if executed directly
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
