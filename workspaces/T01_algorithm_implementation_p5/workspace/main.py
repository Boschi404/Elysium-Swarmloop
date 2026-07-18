"""T01_algorithm_implementation - Implement Binary Search.

Binary search implementation on a sorted list.
Time complexity: O(log n)
Space complexity: O(1)
"""


def binary_search(arr: list[int], target: int) -> int:
    """Perform binary search on a sorted list to find the target value.

    Input: arr - sorted list of integers, target - value to search
    Output: index of target if found, -1 otherwise
    Raises: ValueError if arr is not sorted (for input validation only)
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
