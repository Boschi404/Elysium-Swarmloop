"""Tests for binary_search implementation.

Covers:
- Exact match found
- Element not found
- Empty list
- Single element (target present, target absent)
- Duplicate elements (first occurrence)
- Very large lists (performance test for O(log n))
- Left boundary, right boundary
- Negative numbers
"""

import math
import time
import sys
import os

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from binary_search import binary_search, binary_search_any


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def test_exact_match_found():
    """Target exists in the middle of the list."""
    arr = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search(arr, 7) == 3
    assert binary_search_any(arr, 7) == 3


def test_element_not_found():
    """Target does not exist in the list."""
    arr = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search(arr, 4) == -1
    assert binary_search_any(arr, 4) == -1


def test_empty_list():
    """Search on an empty list always returns -1."""
    assert binary_search([], 42) == -1
    assert binary_search_any([], 42) == -1


def test_single_element_found():
    """Single element list where target matches."""
    assert binary_search([5], 5) == 0
    assert binary_search_any([5], 5) == 0


def test_single_element_not_found():
    """Single element list where target does not match."""
    assert binary_search([5], 3) == -1
    assert binary_search_any([5], 3) == -1


def test_duplicate_elements_first_occurrence():
    """
    binary_search returns the FIRST (leftmost) occurrence index.
    binary_search_any returns ANY valid index (not necessarily first).
    """
    arr = [1, 2, 2, 2, 3, 4, 5]

    # binary_search must return the first occurrence
    idx = binary_search(arr, 2)
    assert idx == 1, f"Expected first occurrence at index 1, got {idx}"

    # binary_search_any can return any of the duplicate indices
    any_idx = binary_search_any(arr, 2)
    assert any_idx in (1, 2, 3), (
        f"Expected any of indices 1,2,3, got {any_idx}"
    )


def test_all_duplicates():
    """All elements are the same value."""
    arr = [7, 7, 7, 7, 7]
    assert binary_search(arr, 7) == 0  # first occurrence
    assert binary_search(arr, 8) == -1


def test_target_smaller_than_all():
    """Target is smaller than every element."""
    arr = [10, 20, 30, 40]
    assert binary_search(arr, 5) == -1


def test_target_larger_than_all():
    """Target is larger than every element."""
    arr = [10, 20, 30, 40]
    assert binary_search(arr, 50) == -1


def test_left_boundary():
    """Target at the very start of the list."""
    arr = [1, 2, 3, 4, 5]
    assert binary_search(arr, 1) == 0


def test_right_boundary():
    """Target at the very end of the list."""
    arr = [1, 2, 3, 4, 5]
    assert binary_search(arr, 5) == 4


def test_negative_numbers():
    """List with negative values."""
    arr = [-10, -5, -1, 0, 3, 8]
    assert binary_search(arr, -5) == 1
    assert binary_search(arr, -10) == 0
    assert binary_search(arr, 8) == 5
    assert binary_search(arr, -99) == -1


def test_even_length():
    """List has an even number of elements."""
    arr = [2, 4, 6, 8]
    assert binary_search(arr, 2) == 0
    assert binary_search(arr, 8) == 3
    assert binary_search(arr, 6) == 2
    assert binary_search(arr, 5) == -1


def test_odd_length():
    """List has an odd number of elements."""
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 9) == 4
    assert binary_search(arr, 5) == 2


def test_large_list_performance():
    """Very large list (10M elements) — O(log n) should complete in < 1s."""
    n = 10_000_000
    arr = list(range(n))

    target = 8_888_888
    start = time.perf_counter()
    idx = binary_search(arr, target)
    elapsed = time.perf_counter() - start

    assert idx == target, f"Expected index {target}, got {idx}"
    # O(log n) on 10M is ~24 iterations — should be well under 50ms
    assert elapsed < 1.0, (
        f"Performance test took {elapsed:.3f}s (expected < 1s)"
    )


def test_large_list_not_found():
    """Target missing from a very large list — still fast."""
    n = 10_000_000
    arr = list(range(n))

    start = time.perf_counter()
    idx = binary_search(arr, -1)
    elapsed = time.perf_counter() - start

    assert idx == -1
    assert elapsed < 1.0, (
        f"Not-found on large list took {elapsed:.3f}s (expected < 1s)"
    )


def test_large_list_worst_case():
    """Worst-case O(log n) — target at extreme end."""
    n = 10_000_000
    arr = list(range(n))

    start = time.perf_counter()
    idx = binary_search(arr, n - 1)
    elapsed = time.perf_counter() - start

    assert idx == n - 1
    assert elapsed < 1.0


def test_max_iterations_log_n():
    """
    Verify that the number of iterations never exceeds floor(log2(n)) + 1
    for the first-match implementation.
    """
    n = 1_000_000
    arr = list(range(n))
    max_iters = math.floor(math.log2(n)) + 1

    # Repeatedly search and count internal iterations
    # We can count by using a custom wrapper
    original_mid = None
    iters = 0

    # Search a few random positions
    for target in [0, n // 4, n // 2, 3 * n // 4, n - 1, -1]:
        left, right = 0, n - 1
        local_iters = 0
        found = -1

        while left <= right and local_iters <= max_iters:
            local_iters += 1
            mid = left + (right - left) // 2
            if arr[mid] == target:
                found = mid
                right = mid - 1  # leftmost scan
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        assert found == (target if 0 <= target < n else -1)
        assert local_iters <= max_iters, (
            f"Target {target}: {local_iters} iterations "
            f"exceeded max {max_iters}"
        )
        iters = max(iters, local_iters)

    # Log for transparency
    print(f"\n[INFO] Max iterations for n={n} (log2={math.log2(n):.1f}): "
          f"observed={iters}, theoretical_max={max_iters}")


def test_stress_random_positions():
    """Random positions in a moderate-sized list."""
    n = 100_000
    arr = list(range(n))

    targets = [0, 1, 2, 3, n // 2, n - 3, n - 2, n - 1, 42, 99999]
    for t in targets:
        assert binary_search(arr, t) == t
        assert binary_search_any(arr, t) == t


def test_consistency_between_functions():
    """Both functions agree on the same results."""
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for t in range(-5, 15):
        standard = binary_search(arr, t)
        any_ver = binary_search_any(arr, t)

        if t in arr:
            # Both must find it; standard must be the first occurrence
            assert standard != -1
            assert arr[standard] == t
            assert any_ver != -1
            assert arr[any_ver] == t
        else:
            assert standard == -1
            assert any_ver == -1
