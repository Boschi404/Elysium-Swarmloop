"""
Binary Search Implementation
============================
Implements binary search on a sorted list with O(log n) time complexity.

Features:
- Exact match finding
- Element not found handling
- Empty list safety
- Single element support
- Duplicate element handling (returns first occurrence)
- Iterative approach (O(1) space, avoids recursion depth limits)
"""

from typing import List, Optional


def binary_search(arr: List[int], target: int) -> int:
    """
    Perform binary search on a sorted list to find the target element.

    Args:
        arr: A sorted list of integers (ascending order).
        target: The integer value to search for.

    Returns:
        The index of the target if found, otherwise -1.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Examples:
        >>> binary_search([1, 2, 3, 4, 5], 3)
        2
        >>> binary_search([1, 2, 3, 4, 5], 6)
        -1
        >>> binary_search([], 1)
        -1
        >>> binary_search([1], 1)
        0
    """
    # Edge case: empty list
    if not arr:
        return -1

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2  # Avoids integer overflow

        if arr[mid] == target:
            # For duplicates, continue searching left for first occurrence
            result = mid
            right = mid - 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_any(arr: List[int], target: int) -> int:
    """
    Standard binary search returning any occurrence (not necessarily the first).

    Faster than first-occurrence variant for targets without duplicates.
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
