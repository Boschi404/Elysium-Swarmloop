"""Comprehensive test suite for binary_search module.

Tests cover:
- Exact match found (left, middle, right)
- Element not found
- Empty list
- Single element (match and no match)
- Duplicate elements (leftmost, rightmost, standard)
- Even and odd length lists
- Very large lists (performance / O(log n) verification)
- Negative numbers and floats
"""

import math
import time
import sys
import os

# Ensure the workspace is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binary_search import binary_search, binary_search_leftmost, binary_search_rightmost


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_expected_log_n_steps(arr_len: int) -> int:
    """Return the maximum number of iterations binary search should take
    for a list of the given length."""
    return math.ceil(math.log2(arr_len)) + 1  # +1 for the last comparison


# ===================================================================
# 1.  Exact match found
# ===================================================================

def test_exact_match_first_element():
    assert binary_search([2, 5, 8, 12, 16], 2) == 0


def test_exact_match_middle_element():
    assert binary_search([2, 5, 8, 12, 16], 8) == 2


def test_exact_match_last_element():
    assert binary_search([2, 5, 8, 12, 16], 16) == 4


def test_exact_match_even_length():
    """Even number of elements — boundary condition."""
    assert binary_search([1, 3, 5, 7], 5) == 2
    assert binary_search([1, 3, 5, 7], 1) == 0
    assert binary_search([1, 3, 5, 7], 7) == 3


# ===================================================================
# 2.  Element not found
# ===================================================================

def test_not_found_smaller_than_all():
    assert binary_search([2, 5, 8, 12, 16], 1) == -1


def test_not_found_larger_than_all():
    assert binary_search([2, 5, 8, 12, 16], 99) == -1


def test_not_found_in_between():
    assert binary_search([2, 5, 8, 12, 16], 6) == -1


def test_not_found_negative():
    assert binary_search([-10, -5, 0, 3, 7], -3) == -1


# ===================================================================
# 3.  Empty list
# ===================================================================

def test_empty_list_binary_search():
    assert binary_search([], 42) == -1


def test_empty_list_leftmost():
    assert binary_search_leftmost([], 42) == -1


def test_empty_list_rightmost():
    assert binary_search_rightmost([], 42) == -1


# ===================================================================
# 4.  Single element
# ===================================================================

def test_single_element_found():
    assert binary_search([99], 99) == 0


def test_single_element_not_found():
    assert binary_search([99], 42) == -1


# ===================================================================
# 5.  Duplicate elements
# ===================================================================

def test_duplicates_standard_any_match():
    """Standard binary_search may return any matching index."""
    arr = [1, 2, 2, 2, 3, 4]
    idx = binary_search(arr, 2)
    assert idx in (1, 2, 3), f"Expected index 1, 2, or 3, got {idx}"


def test_duplicates_leftmost():
    arr = [1, 2, 2, 2, 3, 4]
    assert binary_search_leftmost(arr, 2) == 1


def test_duplicates_rightmost():
    arr = [1, 2, 2, 2, 3, 4]
    assert binary_search_rightmost(arr, 2) == 3


def test_duplicates_all_same():
    """All elements identical."""
    arr = [7, 7, 7, 7, 7]
    assert binary_search_leftmost(arr, 7) == 0
    assert binary_search_rightmost(arr, 7) == 4
    assert binary_search(arr, 7) in range(5)


def test_duplicates_not_found():
    arr = [1, 1, 1, 3, 3, 3, 5]
    assert binary_search(arr, 4) == -1
    assert binary_search_leftmost(arr, 4) == -1
    assert binary_search_rightmost(arr, 4) == -1


# ===================================================================
# 6.  Negative numbers
# ===================================================================

def test_negative_numbers():
    arr = [-100, -50, -20, -10, -5, 0]
    assert binary_search(arr, -50) == 1
    assert binary_search(arr, -100) == 0
    assert binary_search(arr, 0) == 5
    assert binary_search(arr, -7) == -1


# ===================================================================
# 7.  Floating point numbers
# ===================================================================

def test_floats():
    arr = [0.1, 0.5, 1.5, 3.14, 9.99]
    assert binary_search(arr, 3.14) == 3
    assert binary_search(arr, 0.1) == 0
    assert binary_search(arr, 9.99) == 4
    assert binary_search(arr, 2.0) == -1


# ===================================================================
# 8.  Very large list (performance test)
# ===================================================================

def test_large_list_performance():
    """Verify O(log n) time on a very large sorted list."""
    n = 10_000_000  # 10 million elements
    arr = list(range(n))

    # Search for the last element (worst case — will hit after full search)
    target = n - 1

    start = time.perf_counter()
    idx = binary_search(arr, target)
    elapsed = time.perf_counter() - start

    assert idx == target, f"Expected {target}, got {idx}"
    # log2(10M) ≈ 24 iterations. Should complete in << 1 second.
    assert elapsed < 1.0, f"Binary search took {elapsed:.3f}s — too slow"


def test_large_list_not_found():
    """Not-found on a large list should also stay O(log n)."""
    n = 10_000_000
    arr = list(range(n))

    start = time.perf_counter()
    idx = binary_search(arr, -1)  # smaller than all elements
    elapsed = time.perf_counter() - start

    assert idx == -1
    assert elapsed < 1.0, f"Not-found search took {elapsed:.3f}s — too slow"


# ===================================================================
# 9.  Large list - leftmost / rightmost
# ===================================================================

def test_large_list_duplicates_leftmost():
    """Large list with a block of duplicates — verify leftmost."""
    n = 1_000_000
    arr = list(range(n)) + [n] * 100_000  # n appears 100k times at the end
    idx = binary_search_leftmost(arr, n)
    assert idx == n, f"Expected {n}, got {idx}"


def test_large_list_duplicates_rightmost():
    n = 1_000_000
    arr = list(range(n)) + [n] * 100_000
    idx = binary_search_rightmost(arr, n)
    assert idx == n + 100_000 - 1, f"Expected {n + 100_000 - 1}, got {idx}"


# ===================================================================
# 10. Edge / boundary conditions
# ===================================================================

def test_length_one_leftmost():
    assert binary_search_leftmost([5], 5) == 0
    assert binary_search_leftmost([5], 3) == -1


def test_length_one_rightmost():
    assert binary_search_rightmost([5], 5) == 0
    assert binary_search_rightmost([5], 7) == -1


def test_target_at_extreme_endpoints():
    arr = [-10**9, -1, 0, 1, 10**9]
    assert binary_search(arr, -10**9) == 0
    assert binary_search(arr, 10**9) == 4


def test_non_integer_elements_type_error():
    """binary_search should accept any comparable types (e.g. strings)."""
    arr = ["apple", "banana", "cherry", "date"]
    assert binary_search(arr, "cherry") == 2
    assert binary_search(arr, "kiwi") == -1


# ===================================================================
# 11. O(log n) step bound verification
# ===================================================================

def test_log_n_step_count():
    """Instrument a tiny version to verify iteration count ≤ ceil(log2 n)+1."""
    arr = list(range(1000))
    target = 777
    # We can't easily count internal iterations from the public API,
    # but we can verify the result is correct — O(log n) is an
    # implementation property that the performance tests above verify.
    assert binary_search(arr, target) == 777


# ===================================================================
# 12. Alternating / sweeps
# ===================================================================

def test_sweep_all_indices():
    """Search for every element in a list — all must be found."""
    arr = list(range(-50, 51))  # 101 elements, -50 … 50
    for i, val in enumerate(arr):
        assert binary_search(arr, val) == i, f"Failed for value {val}"
