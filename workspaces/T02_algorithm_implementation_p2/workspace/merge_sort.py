"""
merge_sort: O(n log n) stable sorting algorithm.

Implementation details:
  - Top-down recursive merge sort
  - Sorts lists of arbitrary comparable elements
  - Supports a ``key`` parameter (like built-in ``sorted()``)
  - Handles empty lists, single elements, already-sorted, reversed, duplicates
  - Memory: O(n) auxiliary (the standard merge‑sort trade‑off)

  The key-based path pre-computes the key for every element once (matching
  CPython's own ``list.sort`` strategy) so that key calls are never repeated
  inside the merged loops.
"""

from collections.abc import Callable
from typing import Any, Optional


def merge_sort(
    items: list[Any],
    *,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> list[Any]:
    """Return a new list sorted in ascending (or descending) order via merge sort.

    Parameters
    ----------
    items : list[Any]
        The list to sort.  Elements must be comparable to each other (or at
        least comparable through *key*).
    key : callable, optional
        A function of one argument that extracts a comparison key from each
        element, exactly like the *key* argument of the built-in ``sorted()``.
    reverse : bool, default False
        If True, sort in descending order instead of ascending.

    Returns
    -------
    list[Any]
        A new sorted list (the original is not mutated).

    Time  complexity: O(n log n)  — worst / average / best case.
    Space complexity: O(n)        — auxiliary (temporary merged arrays).
    """
    n = len(items)
    if n <= 1:
        return list(items)  # copy -> caller's list is never mutated

    # ── Fast path: no key function ──────────────────────────────
    if key is None:
        if reverse:
            return _merge_sort_impl(items, 0, n, reverse=True)
        return _merge_sort_impl(items, 0, n, reverse=False)

    # ── Key-based path: pre‑compute keys once ───────────────────
    # Build (key, original_index, item) triples so the sort is stable and
    # the merge phase never calls key() again.
    triples = [(key(e), idx, e) for idx, e in enumerate(items)]

    if reverse:
        # Negate reverse: sort by -key (works for numeric keys) or
        # sort triples descending.  We'll use a dedicated desc merge.
        sorted_triples = _merge_sort_triples(triples, 0, n, reverse=True)
    else:
        sorted_triples = _merge_sort_triples(triples, 0, n, reverse=False)

    return [t[2] for t in sorted_triples]


# ══════════════════════════════════════════════════════════════════
# Direct comparison (no key)
# ══════════════════════════════════════════════════════════════════


def _merge_sort_impl(items: list, lo: int, hi: int, reverse: bool) -> list:
    """Return a sorted copy of ``items[lo:hi]``."""
    length = hi - lo
    if length <= 1:
        return [items[lo]] if length == 1 else []

    mid = lo + (length // 2)
    left = _merge_sort_impl(items, lo, mid, reverse)
    right = _merge_sort_impl(items, mid, hi, reverse)

    if reverse:
        return _merge_desc(left, right)
    return _merge_asc(left, right)


def _merge_asc(left: list, right: list) -> list:
    """Merge two sorted lists into a single ascending list."""
    result = []
    i = j = 0
    nl, nr = len(left), len(right)

    while i < nl and j < nr:
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    if i < nl:
        result.extend(left[i:])
    if j < nr:
        result.extend(right[j:])
    return result


def _merge_desc(left: list, right: list) -> list:
    """Merge two sorted lists into a single descending list."""
    result = []
    i = j = 0
    nl, nr = len(left), len(right)

    while i < nl and j < nr:
        if left[i] >= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    if i < nl:
        result.extend(left[i:])
    if j < nr:
        result.extend(right[j:])
    return result


# ══════════════════════════════════════════════════════════════════
# Key-based comparison (uses (key, index, item) triples)
# ══════════════════════════════════════════════════════════════════


def _merge_sort_triples(
    triples: list[tuple], lo: int, hi: int, reverse: bool
) -> list[tuple]:
    """Return sorted copy of triples[lo:hi] (by key)."""
    length = hi - lo
    if length <= 1:
        return [triples[lo]] if length == 1 else []

    mid = lo + (length // 2)
    left = _merge_sort_triples(triples, lo, mid, reverse)
    right = _merge_sort_triples(triples, mid, hi, reverse)

    if reverse:
        return _merge_triples_desc(left, right)
    return _merge_triples_asc(left, right)


def _merge_triples_asc(left: list[tuple], right: list[tuple]) -> list[tuple]:
    """Merge two key-sorted triple lists ascending."""
    result = []
    i = j = 0
    nl, nr = len(left), len(right)

    while i < nl and j < nr:
        # Compare by key (idx 0).  On tie, compare by original index (idx 1)
        # to guarantee stability.
        if left[i][0] < right[j][0] or (
            left[i][0] == right[j][0] and left[i][1] <= right[j][1]
        ):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    if i < nl:
        result.extend(left[i:])
    if j < nr:
        result.extend(right[j:])
    return result


def _merge_triples_desc(left: list[tuple], right: list[tuple]) -> list[tuple]:
    """Merge two key-sorted triple lists descending."""
    result = []
    i = j = 0
    nl, nr = len(left), len(right)

    while i < nl and j < nr:
        if left[i][0] > right[j][0] or (
            left[i][0] == right[j][0] and left[i][1] <= right[j][1]
        ):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    if i < nl:
        result.extend(left[i:])
    if j < nr:
        result.extend(right[j:])
    return result
