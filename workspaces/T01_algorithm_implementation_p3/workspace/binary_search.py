"""
Binary search implementation on a sorted list.

Complexity: O(log n) time, O(1) space.
Returns the index of the target element, or -1 if not found.
"""


def binary_search(arr: list[int], target: int) -> int:
    """
    Perform binary search on a sorted list of integers.

    Args:
        arr: A sorted (ascending) list of integers.
        target: The integer value to search for.

    Returns:
        The index of the target if found, otherwise -1.
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoids overflow
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
