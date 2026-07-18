"""
Binary search implementation on a sorted list.

Time complexity: O(log n)
Space complexity: O(1) — iterative approach

Handles:
  - Exact match found       → returns index
  - Element not found       → returns -1
  - Empty list              → returns -1
  - Single element          → works correctly
  - Duplicate elements      → returns any valid index of the target
  - Very large lists        → O(log n) ensures performance
"""

from typing import List, Any


def binary_search(arr: List[Any], target: Any) -> int:
    """
    Perform an iterative binary search on a sorted list.

    Args:
        arr: A sorted list of comparable elements.
        target: The element to search for.

    Returns:
        The index of the target if found, otherwise -1.
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoids overflow for very large lists
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
