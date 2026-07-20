"""Binary search implementation on a sorted list.

Returns the index of the target element, or -1 if not found.
Time complexity: O(log n)
Space complexity: O(1)
"""


def binary_search(arr: list, target: int) -> int:
    """Perform binary search on a sorted list.

    Args:
        arr: Sorted list of integers (ascending order).
        target: The value to search for.

    Returns:
        Index of the target if found, otherwise -1.
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoid integer overflow
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_recursive(arr: list, target: int) -> int:
    """Recursive binary search. Provided as an alternative implementation.

    Args:
        arr: Sorted list of integers (ascending order).
        target: The value to search for.

    Returns:
        Index of the target if found, otherwise -1.
    """
    if not arr:
        return -1

    def _search(left: int, right: int) -> int:
        if left > right:
            return -1
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            return _search(mid + 1, right)
        else:
            return _search(left, mid - 1)

    return _search(0, len(arr) - 1)


def find_first_occurrence(arr: list, target: int) -> int:
    """Binary search for the first (leftmost) occurrence of target.

    Useful when the list contains duplicate elements and the leftmost
    index is required. Otherwise equivalent to binary_search().

    Args:
        arr: Sorted list of integers (ascending order).
        target: The value to search for.

    Returns:
        Index of the first occurrence if found, otherwise -1.
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1  # keep searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def find_last_occurrence(arr: list, target: int) -> int:
    """Binary search for the last (rightmost) occurrence of target.

    Args:
        arr: Sorted list of integers (ascending order).
        target: The value to search for.

    Returns:
        Index of the last occurrence if found, otherwise -1.
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            left = mid + 1  # keep searching right
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
