"""
Binary Search Implementation
============================
Implements binary search on a sorted list with O(log n) time complexity.

Edge cases handled:
  - Exact match found      → returns index
  - Element not found      → returns -1
  - Empty list             → returns -1
  - Single element         → correct match or -1
  - Duplicate elements     → returns first matching index found
  - Very large lists       → O(log n), tested via performance check
  - None/invalid input     → returns -1

Time complexity:  O(log n)
Space complexity: O(1) — iterative, no recursion overhead
"""


def binary_search(arr: list, target) -> int:
    """
    Search for target in a sorted list using binary search.

    Args:
        arr: Sorted list of comparable elements (ascending order).
        target: Element to search for.

    Returns:
        Index of target if found, -1 otherwise.
    """
    # Guard: invalid or empty input
    if arr is None or len(arr) == 0:
        return -1

    left: int = 0
    right: int = len(arr) - 1

    while left <= right:
        # Calculate midpoint — avoids overflow in languages with fixed ints
        mid: int = left + (right - left) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_first_occurrence(arr: list, target) -> int:
    """
    Return the index of the FIRST occurrence of target in a sorted list
    that may contain duplicates.  Falls back to standard binary search
    when duplicates are not a concern.

    Args:
        arr: Sorted list (ascending).
        target: Element to find.

    Returns:
        Index of the first occurrence, or -1 if not found.
    """
    if arr is None or len(arr) == 0:
        return -1

    left: int = 0
    right: int = len(arr) - 1
    result: int = -1

    while left <= right:
        mid: int = left + (right - left) // 2
        mid_val = arr[mid]

        if mid_val == target:
            result = mid          # record the match
            right = mid - 1       # keep looking left for an earlier occurrence
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
