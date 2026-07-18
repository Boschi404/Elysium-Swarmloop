"""
merge_sort — O(n log n) merge sort implementation.

Features:
  - Sorts lists/iterables in ascending or descending order
  - Supports a `key` parameter (like built-in sorted()) via decorate-sort-undecorate
  - Handles empty list, single element, already sorted, reverse sorted, duplicates
  - Efficient for large lists (100k+ elements) — iterative bottom-up avoids recursion depth
  - Stable sort (equal elements retain original relative order)
"""

from collections.abc import Callable, Iterable
from typing import Any, Optional


def merge_sort(
    iterable: Iterable[Any],
    *,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> list[Any]:
    """
    Sort *iterable* using the merge sort algorithm (O(n log n) worst case).

    Parameters
    ----------
    iterable:
        Any Python iterable to sort.
    key:
        Optional callable that extracts a comparison key from each element.
        Behaves like ``sorted(..., key=...)``.
    reverse:
        If True, sort in descending order (default: ascending).

    Returns
    -------
    list
        A *new* sorted list (the original iterable is not modified).

    Examples
    --------
    >>> merge_sort([3, 1, 4, 1, 5, 9])
    [1, 1, 3, 4, 5, 9]
    >>> merge_sort([3, 1, 4], reverse=True)
    [4, 3, 1]
    >>> merge_sort(['abc', 'a', 'xy'], key=len)
    ['a', 'xy', 'abc']
    """
    items = list(iterable)
    n = len(items)

    # Trivial cases — nothing to sort
    if n <= 1:
        return items

    if key is not None:
        return _merge_sort_keyed(items, key, reverse)
    return _merge_sort_direct(items, reverse)


# ---------------------------------------------------------------------------
# Direct comparison (no key)
# ---------------------------------------------------------------------------

def _merge_sort_direct(lst: list[Any], reverse: bool) -> list[Any]:
    """Bottom-up (iterative) merge sort — avoids Python recursion overhead."""
    n = len(lst)
    # Work with a copy so we never mutate the caller's list
    result = lst[:]

    # Width = size of sub-lists being merged at each level
    width = 1
    while width < n:
        for left_start in range(0, n, 2 * width):
            mid = left_start + width
            right_end = min(left_start + 2 * width, n)

            if mid >= n:
                continue  # nothing to merge this pair

            # Merge result[left_start:right_end] using the temporary buffer
            _merge_direct_inplace(result, left_start, mid, right_end, reverse)
        width *= 2

    return result


def _merge_direct_inplace(
    lst: list[Any],
    left: int,
    mid: int,
    right: int,
    reverse: bool,
) -> None:
    """
    Merge two sorted slices ``lst[left:mid]`` and ``lst[mid:right]`` in-place.
    Both slices are already sorted in the final order.
    """
    left_slice = lst[left:mid]
    right_slice = lst[mid:right]

    i = j = 0
    k = left
    len_l = len(left_slice)
    len_r = len(right_slice)

    if reverse:
        # Descending: take the larger element first
        while i < len_l and j < len_r:
            if left_slice[i] >= right_slice[j]:
                lst[k] = left_slice[i]
                i += 1
            else:
                lst[k] = right_slice[j]
                j += 1
            k += 1
    else:
        # Ascending: take the smaller element first
        while i < len_l and j < len_r:
            if left_slice[i] <= right_slice[j]:
                lst[k] = left_slice[i]
                i += 1
            else:
                lst[k] = right_slice[j]
                j += 1
            k += 1

    # Drain remaining elements from whichever side still has them
    while i < len_l:
        lst[k] = left_slice[i]
        i += 1
        k += 1
    while j < len_r:
        lst[k] = right_slice[j]
        j += 1
        k += 1


# ---------------------------------------------------------------------------
# Key-based sort  (decorate → sort → undecorate)
# ---------------------------------------------------------------------------

def _merge_sort_keyed(
    lst: list[Any],
    key: Callable[[Any], Any],
    reverse: bool,
) -> list[Any]:
    """
    Sort *lst* using *key* via decorate-sort-undecorate.
    We attach the original index for guaranteed stability.
    """
    # Decorate: (key_value, original_index, original_item)
    decorated = [(key(item), idx, item) for idx, item in enumerate(lst)]
    # Sort by key value; if keys tie, by original index (stable)
    decorated = _merge_sort_decorated(decorated, reverse)
    # Undecorate
    return [item for _, _, item in decorated]


def _merge_sort_decorated(
    lst: list[tuple[Any, int, Any]],
    reverse: bool,
) -> list[tuple[Any, int, Any]]:
    """Bottom-up merge sort for decorated tuples ``(key, idx, item)``."""
    n = len(lst)
    result = lst[:]

    width = 1
    while width < n:
        for left_start in range(0, n, 2 * width):
            mid = left_start + width
            right_end = min(left_start + 2 * width, n)
            if mid >= n:
                continue
            _merge_decorated_inplace(result, left_start, mid, right_end, reverse)
        width *= 2

    return result


def _merge_decorated_inplace(
    lst: list[tuple[Any, int, Any]],
    left: int,
    mid: int,
    right: int,
    reverse: bool,
) -> None:
    """In-place merge for decorated tuples."""
    left_slice = lst[left:mid]
    right_slice = lst[mid:right]

    i = j = 0
    k = left
    len_l = len(left_slice)
    len_r = len(right_slice)

    if reverse:
        # Descending: larger key (or same key, smaller index) first
        while i < len_l and j < len_r:
            li_key, li_idx, _ = left_slice[i]
            rj_key, rj_idx, _ = right_slice[j]
            if li_key > rj_key or (li_key == rj_key and li_idx <= rj_idx):
                lst[k] = left_slice[i]
                i += 1
            else:
                lst[k] = right_slice[j]
                j += 1
            k += 1
    else:
        # Ascending: smaller key (or same key, smaller index) first
        while i < len_l and j < len_r:
            li_key, li_idx, _ = left_slice[i]
            rj_key, rj_idx, _ = right_slice[j]
            if li_key < rj_key or (li_key == rj_key and li_idx <= rj_idx):
                lst[k] = left_slice[i]
                i += 1
            else:
                lst[k] = right_slice[j]
                j += 1
            k += 1

    while i < len_l:
        lst[k] = left_slice[i]
        i += 1
        k += 1
    while j < len_r:
        lst[k] = right_slice[j]
        j += 1
        k += 1
