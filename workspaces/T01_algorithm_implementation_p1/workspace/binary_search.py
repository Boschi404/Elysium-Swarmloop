"""Binary search implementation on a sorted list.

Time complexity: O(log n)
Space complexity: O(1) iterative, O(log n) recursive
"""


def binary_search(arr: list, target: int) -> int:
    """Perform binary search on a sorted list.

    Args:
        arr: Sorted list of elements (ascending order).
        target: Element to search for.

    Returns:
        Index of the target if found, otherwise -1.
    """
    low, high = 0, len(arr) - 1

    while low <= high:
        mid = low + (high - low) // 2  # avoids overflow in other languages
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def binary_search_recursive(arr: list, target: int, low: int = None, high: int = None) -> int:
    """Recursive binary search — convenience wrapper."""
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1

    if low > high:
        return -1

    mid = low + (high - low) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, high)
    else:
        return binary_search_recursive(arr, target, low, mid - 1)


def find_first_occurrence(arr: list, target: int) -> int:
    """Return the index of the FIRST occurrence of target in a sorted list
    with duplicates, or -1 if not found.

    Still O(log n) — continues left after finding a match.
    """
    low, high = 0, len(arr) - 1
    result = -1

    while low <= high:
        mid = low + (high - low) // 2

        if arr[mid] == target:
            result = mid
            high = mid - 1  # keep searching left
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return result


def find_last_occurrence(arr: list, target: int) -> int:
    """Return the index of the LAST occurrence of target in a sorted list
    with duplicates, or -1 if not found.

    Still O(log n) — continues right after finding a match.
    """
    low, high = 0, len(arr) - 1
    result = -1

    while low <= high:
        mid = low + (high - low) // 2

        if arr[mid] == target:
            result = mid
            low = mid + 1  # keep searching right
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return result
