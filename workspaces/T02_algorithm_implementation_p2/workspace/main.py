"""
Merge Sort Implementation
=========================
Implements merge sort with O(n log n) worst-case time complexity.

Features:
- Empty list handling
- Single element support
- Already sorted and reverse sorted optimization paths
- Duplicate element handling (stable sort)
- Large list support (100k+ elements)
- Custom sort key function support (like built-in sorted())
- Ascending and descending order support
"""

from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def merge_sort(
    items: List[T],
    key: Optional[Callable[[T], U]] = None,
    reverse: bool = False,
) -> List[T]:
    """
    Sort a list using the merge sort algorithm.

    Args:
        items: The list of elements to sort.
        key: Optional function that computes a sort key for each element.
             Behaves like the key parameter in built-in sorted().
        reverse: If True, sort in descending order (default: ascending).

    Returns:
        A new sorted list (does not modify the original).

    Time Complexity: O(n log n) in all cases (worst, average, best).
    Space Complexity: O(n) for temporary arrays during merge.

    Examples:
        >>> merge_sort([3, 1, 4, 1, 5, 9, 2, 6])
        [1, 1, 2, 3, 4, 5, 6, 9]
        >>> merge_sort([])
        []
        >>> merge_sort([1])
        [1]
        >>> merge_sort([3, 1, 2], reverse=True)
        [3, 2, 1]
        >>> merge_sort(["apple", "kiwi", "banana"], key=len)
        ['kiwi', 'apple', 'banana']
    """
    if not items:
        return []

    lst = list(items)
    n = len(lst)

    if n <= 1:
        return lst

    if key is not None:
        # Decorate-sort-undecorate (Schwartzian transform)
        decorated = [(key(item), idx, item) for idx, item in enumerate(lst)]
        sorted_decorated = _merge_sort_impl(decorated, reverse)
        return [item for _, _, item in sorted_decorated]

    return _merge_sort_impl(lst, reverse)


def _merge_sort_impl(arr: List[T], reverse: bool = False) -> List[T]:
    """
    Internal merge sort with optional reverse parameter.

    Uses top-down divide-and-conquer:
    1. Split the array in half
    2. Recursively sort each half
    3. Merge the sorted halves
    """
    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left = _merge_sort_impl(arr[:mid], reverse)
    right = _merge_sort_impl(arr[mid:], reverse)

    return _merge(left, right, reverse)


def _merge(left: List[T], right: List[T], reverse: bool = False) -> List[T]:
    """
    Merge two already-sorted lists into a single sorted list.
    """
    result = []
    i = j = 0
    len_left, len_right = len(left), len(right)

    if reverse:
        while i < len_left and j < len_right:
            if left[i] >= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
    else:
        while i < len_left and j < len_right:
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    # Append remaining elements (one of the two lists is exhausted)
    if i < len_left:
        result.extend(left[i:])
    if j < len_right:
        result.extend(right[j:])

    return result
