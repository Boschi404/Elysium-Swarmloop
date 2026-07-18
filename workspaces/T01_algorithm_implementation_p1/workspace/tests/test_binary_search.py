"""Tests for binary search implementation — covers all required edge cases."""
import sys
import os
import math
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from binary_search import (
    binary_search,
    binary_search_recursive,
    find_first_occurrence,
    find_last_occurrence,
)


# ── Standard iterative binary_search ──────────────────────────────────────


def test_exact_match():
    """Target present in the middle of the list."""
    arr = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search(arr, 7) == 3


def test_element_not_found():
    """Target not in the list → -1."""
    arr = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search(arr, 4) == -1


def test_empty_list():
    """Empty list → -1."""
    assert binary_search([], 42) == -1


def test_single_element_found():
    """Single-element list, target matches."""
    assert binary_search([42], 42) == 0


def test_single_element_not_found():
    """Single-element list, target does not match."""
    assert binary_search([42], 1) == -1


def test_target_at_start():
    """Target is the first element."""
    arr = [2, 4, 6, 8, 10]
    assert binary_search(arr, 2) == 0


def test_target_at_end():
    """Target is the last element."""
    arr = [2, 4, 6, 8, 10]
    assert binary_search(arr, 10) == 4


def test_negative_numbers():
    """Works with negative values."""
    arr = [-10, -5, -1, 0, 3, 8]
    assert binary_search(arr, -5) == 1
    assert binary_search(arr, -10) == 0
    assert binary_search(arr, 8) == 5
    assert binary_search(arr, -2) == -1


def test_duplicates_returns_any():
    """With duplicates, standard binary search returns an arbitrary valid index."""
    arr = [1, 2, 2, 2, 3, 4]
    idx = binary_search(arr, 2)
    # must be one of the valid positions
    assert idx in {1, 2, 3}, f"Expected one of [1,2,3], got {idx}"


def test_large_list_performance():
    """Very large list (1M elements) must complete in < 0.5 seconds."""
    n = 1_000_000
    arr = list(range(n))
    target = 876_543

    start = time.perf_counter()
    idx = binary_search(arr, target)
    elapsed = time.perf_counter() - start

    assert idx == target, f"Expected {target}, got {idx}"
    assert elapsed < 0.5, f"Took {elapsed:.3f}s, expected < 0.5s"


def test_large_list_first_element():
    """First element in large list."""
    arr = list(range(1_000_000))
    assert binary_search(arr, 0) == 0


def test_large_list_last_element():
    """Last element in large list."""
    arr = list(range(1_000_000))
    assert binary_search(arr, 999_999) == 999_999


def test_large_list_not_found():
    """Target beyond the large list bounds."""
    arr = list(range(1_000_000))
    assert binary_search(arr, -1) == -1
    assert binary_search(arr, 1_500_000) == -1


# ── Recursive variant ─────────────────────────────────────────────────────


def test_recursive_exact_match():
    assert binary_search_recursive([1, 3, 5, 7, 9], 5) == 2


def test_recursive_not_found():
    assert binary_search_recursive([1, 3, 5, 7, 9], 6) == -1


def test_recursive_empty():
    assert binary_search_recursive([], 1) == -1


def test_recursive_single():
    assert binary_search_recursive([99], 99) == 0
    assert binary_search_recursive([99], 1) == -1


# ── First / last occurrence (duplicates) ──────────────────────────────────


def test_first_occurrence():
    arr = [1, 2, 2, 2, 3, 4, 5]
    assert find_first_occurrence(arr, 2) == 1


def test_last_occurrence():
    arr = [1, 2, 2, 2, 3, 4, 5]
    assert find_last_occurrence(arr, 2) == 3


def test_first_last_single_occurrence():
    """No duplicates → first == last."""
    arr = [1, 3, 5, 7]
    assert find_first_occurrence(arr, 5) == 2
    assert find_last_occurrence(arr, 5) == 2


def test_first_not_found():
    assert find_first_occurrence([1, 2, 3], 4) == -1


def test_last_not_found():
    assert find_last_occurrence([1, 2, 3], 4) == -1


# ── Edge: all elements identical ──────────────────────────────────────────


def test_all_identical():
    arr = [7, 7, 7, 7, 7]
    assert binary_search(arr, 7) in {0, 1, 2, 3, 4}
    assert find_first_occurrence(arr, 7) == 0
    assert find_last_occurrence(arr, 7) == 4


# ── Edge: strings ─────────────────────────────────────────────────────────


def test_strings():
    arr = sorted(["apple", "banana", "cherry", "date", "elderberry"])
    assert binary_search(arr, "cherry") == 2
    assert binary_search(arr, "fig") == -1


# ── O(log n) time complexity verification ────────────────────────────────


def test_log_n_complexity():
    """Verify that the algorithm runs in O(log n) by comparing
    two large lists differing by a factor of 1000 in size.
    """
    n_small = 10_000
    n_large = 10_000_000
    target = n_large // 2

    arr_small = list(range(n_small))
    arr_large = list(range(n_large))

    # The ratio of step counts should be ~log(n_large)/log(n_small) ≈ 2
    # Measure total time; with O(log n) the large list is ~2× slower, not 1000×
    start = time.perf_counter()
    binary_search(arr_small, target)
    small_time = time.perf_counter() - start

    start = time.perf_counter()
    binary_search(arr_large, target)
    large_time = time.perf_counter() - start

    ratio = large_time / (small_time + 1e-12)
    assert ratio < 50, (
        f"Time ratio large/small = {ratio:.1f}, expected < 50 "
        f"(O(log n) should grow ~2×, not 1000×)"
    )
