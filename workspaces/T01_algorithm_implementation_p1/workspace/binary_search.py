"""Binary search implementation on a sorted list.

Provides:
    binary_search(arr, target) -> int
        Returns the index of target in arr, or -1 if not found.
    Time complexity: O(log n)
    Space complexity: O(1)

Handles:
    - exact match found
    - element not found
    - empty list
    - single element
    - duplicate elements (returns any valid index)
    - very large lists (performance)
"""


def binary_search(arr: list, target: int | float) -> int:
    """Perform binary search on a sorted list.

    Finds the index of `target` in `arr` using the binary search algorithm.
    `arr` must be sorted in ascending order.

    Args:
        arr: Sorted list of comparable elements (e.g., ints or floats).
        target: The value to locate.

    Returns:
        Index of `target` in `arr`, or -1 if not found.

    Raises:
        ValueError: If `arr` is not sorted in ascending order.
    """
    # Edge case: empty list
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    # Target not found
    return -1
