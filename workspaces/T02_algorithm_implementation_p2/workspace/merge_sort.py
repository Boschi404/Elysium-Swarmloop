"""
Merge Sort implementation.

Sorts lists in ascending (or descending) order using the merge sort algorithm.
O(n log n) worst-case time complexity.
"""


def merge_sort(arr, key=None, reverse=False):
    """
    Sort a list using the merge sort algorithm.

    Args:
        arr:      The list to sort.
        key:      Function that transforms each element before comparison
                  (like built-in sorted() key parameter).
        reverse:  If True, sort in descending order. Default: ascending.

    Returns:
        A new sorted list (the original is not modified).

    Raises:
        TypeError: If arr is not a list.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list")

    if not arr:
        return []

    if key is None:
        return _merge_sort(arr, reverse)

    # Decorate-sort-undecorate: call key() once per element
    decorated = [(key(item), item) for item in arr]
    sorted_decorated = _merge_sort(decorated, reverse)
    return [item for _, item in sorted_decorated]


def _merge_sort(arr, reverse=False):
    """Recursive merge sort on an array of comparable elements."""
    if len(arr) <= 1:
        return arr[:]

    mid = len(arr) // 2
    left = _merge_sort(arr[:mid], reverse)
    right = _merge_sort(arr[mid:], reverse)
    return _merge(left, right, reverse)


def _merge(left, right, reverse=False):
    """Merge two sorted lists into a single sorted list."""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if reverse:
            condition = left[i] >= right[j]
        else:
            condition = left[i] <= right[j]

        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements
    if i < len(left):
        result.extend(left[i:])
    if j < len(right):
        result.extend(right[j:])

    return result
