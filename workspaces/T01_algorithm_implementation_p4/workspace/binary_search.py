"""
Binary Search Algorithm — O(log n) time complexity.

Implements standard binary search on a sorted list with comprehensive
edge case handling: empty list, single element, duplicates, not found,
performance on very large lists.

Functions:
    binary_search(arr, target) -> int
        Standard binary search. Returns the index of any match, or -1.

    binary_search_leftmost(arr, target) -> int
        Returns the first (leftmost) occurrence index, or -1.

    binary_search_rightmost(arr, target) -> int
        Returns the last (rightmost) occurrence index, or -1.
"""

from typing import List, Union

# Type alias for clarity
Numeric = Union[int, float]


def binary_search(arr: List[Numeric], target: Numeric) -> int:
    """Standard binary search on a sorted list.

    Returns the index of the target if found, or -1 if not found.
    If duplicates exist, any matching index may be returned (implementation-dependent).

    Time: O(log n)
    Space: O(1)

    Input: arr — sorted list of numbers (ascending).
           target — value to search for.
    Output: int index (0-based) or -1.
    Raises: nothing (catches edge cases gracefully).
    """
    # Edge case: empty list
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoid overflow compared to (left+right)//2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_leftmost(arr: List[Numeric], target: Numeric) -> int:
    """Binary search returning the leftmost (first) occurrence of target.

    Useful when the list contains duplicates and the first index is desired.
    Returns -1 if target is not found.

    Time: O(log n)
    Space: O(1)
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        mid_val = arr[mid]

        if mid_val == target:
            result = mid
            right = mid - 1  # continue searching in left half
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_rightmost(arr: List[Numeric], target: Numeric) -> int:
    """Binary search returning the rightmost (last) occurrence of target.

    Useful when the list contains duplicates and the last index is desired.
    Returns -1 if target is not found.

    Time: O(log n)
    Space: O(1)
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        mid_val = arr[mid]

        if mid_val == target:
            result = mid
            left = mid + 1  # continue searching in right half
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
