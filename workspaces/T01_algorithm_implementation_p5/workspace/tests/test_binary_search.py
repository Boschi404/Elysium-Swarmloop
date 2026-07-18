"""
Comprehensive test suite for binary_search.

Covers:
  - Exact match found
  - Element not found
  - Empty list
  - Single element
  - Duplicate elements
  - Very large lists (performance & correctness)
  - Edge cases (negatives, strings)
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from binary_search import binary_search


# ── Exact match found ──────────────────────────────────────────────

def test_exact_match_start():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_exact_match_middle():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_exact_match_end():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_exact_match_left_of_center():
    assert binary_search([1, 3, 5, 7, 9], 3) == 1


def test_exact_match_right_of_center():
    assert binary_search([1, 3, 5, 7, 9], 7) == 3


# ── Element not found ──────────────────────────────────────────────

def test_not_found_below_all():
    assert binary_search([1, 3, 5, 7, 9], 0) == -1


def test_not_found_above_all():
    assert binary_search([1, 3, 5, 7, 9], 10) == -1


def test_not_found_between_elements():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1


def test_not_found_negative_list():
    assert binary_search([-10, -5, 0, 5, 10], -3) == -1


# ── Empty list ─────────────────────────────────────────────────────

def test_empty_list():
    assert binary_search([], 42) == -1


# ── Single element ─────────────────────────────────────────────────

def test_single_element_found():
    assert binary_search([42], 42) == 0


def test_single_element_not_found():
    assert binary_search([42], 7) == -1


# ── Duplicate elements ─────────────────────────────────────────────

def test_duplicates_found():
    # Should return a valid index for the target
    idx = binary_search([1, 2, 2, 2, 3, 4], 2)
    assert idx in (1, 2, 3)


def test_duplicates_all_same():
    idx = binary_search([5, 5, 5, 5, 5], 5)
    assert 0 <= idx <= 4


def test_duplicates_not_found():
    assert binary_search([1, 1, 2, 2, 3, 3], 4) == -1


# ── Negative numbers ───────────────────────────────────────────────

def test_negative_numbers():
    assert binary_search([-50, -20, -10, -5, 0], -10) == 2


def test_all_negative():
    assert binary_search([-9, -7, -5, -3, -1], -5) == 2


def test_not_found_all_negative():
    assert binary_search([-9, -7, -5, -3, -1], -2) == -1


# ── Strings (comparable types) ─────────────────────────────────────

def test_strings():
    names = sorted(["alice", "bob", "charlie", "diana"])
    assert binary_search(names, "charlie") == 2


def test_string_not_found():
    names = sorted(["alice", "bob", "charlie", "diana"])
    assert binary_search(names, "eve") == -1


# ── Floats ─────────────────────────────────────────────────────────

def test_floats():
    assert binary_search([1.1, 2.2, 3.3, 4.4], 3.3) == 2


# ── Very large list (performance test) ─────────────────────────────

def test_very_large_list_correctness():
    n = 1_000_000
    arr = list(range(n))
    # target at start
    assert binary_search(arr, 0) == 0
    # target at end
    assert binary_search(arr, n - 1) == n - 1
    # target in middle
    assert binary_search(arr, 500_000) == 500_000
    # target not found (below)
    assert binary_search(arr, -1) == -1
    # target not found (above)
    assert binary_search(arr, n) == -1


def test_very_large_list_performance():
    """Binary search on 10M elements must complete in < 2 seconds."""
    n = 10_000_000
    arr = list(range(n))
    start = time.perf_counter()
    # search for a value near the end (worst-case traversal depth)
    result = binary_search(arr, n - 1)
    elapsed = time.perf_counter() - start

    assert result == n - 1
    assert elapsed < 2.0, f"Binary search took {elapsed:.3f}s on 10M elements"


# ── Even-length lists ──────────────────────────────────────────────

def test_even_length_found():
    assert binary_search([2, 4, 6, 8], 6) == 2


def test_even_length_not_found():
    assert binary_search([2, 4, 6, 8], 5) == -1


# ── Odd-length lists ───────────────────────────────────────────────

def test_odd_length_found():
    assert binary_search([1, 3, 5, 7, 9], 7) == 3


# ── Two-element lists ──────────────────────────────────────────────

def test_two_elements_first():
    assert binary_search([10, 20], 10) == 0


def test_two_elements_second():
    assert binary_search([10, 20], 20) == 1


def test_two_elements_not_found():
    assert binary_search([10, 20], 15) == -1
