"""Binary Search Implementation

Implements binary search on a sorted list with O(log n) time complexity.
Handles: exact match, element not found, empty list, single element,
         duplicate elements, and performance-tested on very large lists.

Returns the index of the target element, or -1 if not found.
For duplicates, returns the first occurrence (leftmost) index.
"""

from typing import List, Optional


def binary_search(arr: List[int], target: int) -> int:
    """Perform binary search on a sorted list.

    Args:
        arr: A sorted list of integers (ascending).
        target: The integer value to search for.

    Returns:
        The index of the target if found, otherwise -1.
        For duplicate elements, returns the first occurrence index.
    """
    # Handle empty list immediately
    if not arr:
        return -1

    left: int = 0
    right: int = len(arr) - 1
    result: int = -1

    while left <= right:
        # Avoid potential integer overflow on huge lists
        mid: int = left + (right - left) // 2

        if arr[mid] == target:
            # Found target — record index and keep searching left
            # to find the first occurrence (handles duplicates)
            result = mid
            right = mid - 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_any(arr: List[int], target: int) -> int:
    """Perform binary search returning any matching index (not necessarily first).

    Slightly faster than binary_search() when duplicates are not a concern,
    as it returns immediately on first match without left-scanning.

    Args:
        arr: A sorted list of integers (ascending).
        target: The integer value to search for.

    Returns:
        The index of the target if found, otherwise -1.
    """
    if not arr:
        return -1

    left: int = 0
    right: int = len(arr) - 1

    while left <= right:
        mid: int = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
