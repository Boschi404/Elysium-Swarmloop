"""
Implementation of Merge Sort algorithm.

Sorts lists of integers (or any comparable items) in ascending order.
O(n log n) worst-case time complexity, O(n) auxiliary space.
Supports a key parameter for custom sort keys (like built-in sorted()).
"""

from collections.abc import Callable
from typing import Any


def merge_sort(items: list, key: Callable[[Any], Any] | None = None,
               reverse: bool = False) -> list:
    """
    Sort a list using the merge sort algorithm.

    Args:
        items: List of comparable elements to sort.
        key: Optional function that transforms each element before comparison.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list.

    Raises:
        TypeError: If items is not a list or elements cannot be compared.

    Examples:
        >>> merge_sort([3, 1, 4, 1, 5, 9, 2, 6])
        [1, 1, 2, 3, 4, 5, 6, 9]
        >>> merge_sort([], key=lambda x: -x)
        []
        >>> merge_sort([3, 1, 2], reverse=True)
        [3, 2, 1]
    """
    if not isinstance(items, list):
        raise TypeError(f"Expected a list, got {type(items).__name__}")

    # Work on a copy to avoid mutating the original list
    items = items.copy()
    n = len(items)

    # Handle empty and single-element lists (already sorted)
    if n <= 1:
        return items

    def compare(a: Any, b: Any) -> bool:
        """Return True if a should come before b in the sorted order."""
        va = key(a) if key is not None else a
        vb = key(b) if key is not None else b
        return va < vb if not reverse else va > vb

    # Allocate a single auxiliary array to avoid repeated allocations,
    # improving performance on large inputs while maintaining O(n) aux space.
    aux = [None] * n

    # Bottom-up iterative merge sort for O(log n) stack-space overhead
    # and better performance on large lists.
    width = 1
    while width < n:
        for left in range(0, n, 2 * width):
            mid = min(left + width, n)
            right = min(left + 2 * width, n)

            # Merge items[left:mid] and items[mid:right] into aux
            i, j, k = left, mid, left
            while i < mid and j < right:
                if compare(items[i], items[j]):
                    aux[k] = items[i]
                    i += 1
                else:
                    aux[k] = items[j]
                    j += 1
                k += 1

            # Copy remaining elements from the left half
            while i < mid:
                aux[k] = items[i]
                i += 1
                k += 1

            # Copy remaining elements from the right half
            while j < right:
                aux[k] = items[j]
                j += 1
                k += 1

            # Copy merged segment back to items
            for idx in range(left, right):
                items[idx] = aux[idx]

        width *= 2

    return items


# Expose the function as 'sort' for convenience
sort = merge_sort
