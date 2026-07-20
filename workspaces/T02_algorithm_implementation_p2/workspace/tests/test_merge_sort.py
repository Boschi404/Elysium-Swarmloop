"""Comprehensive test suite for merge_sort."""

import copy
import random
import sys
import time

from merge_sort import merge_sort


# ── Basic cases ──────────────────────────────────────────────────────────

def test_empty_list() -> None:
    assert merge_sort([]) == []


def test_single_element() -> None:
    assert merge_sort([42]) == [42]


def test_two_elements_sorted() -> None:
    assert merge_sort([1, 2]) == [1, 2]


def test_two_elements_reversed() -> None:
    assert merge_sort([2, 1]) == [1, 2]


# ── General cases ────────────────────────────────────────────────────────

def test_already_sorted() -> None:
    data = list(range(50))
    assert merge_sort(data) == data


def test_reverse_sorted() -> None:
    assert merge_sort(list(reversed(range(50)))) == list(range(50))


def test_duplicates() -> None:
    data = [5, 1, 3, 3, 2, 5, 1, 4]
    assert merge_sort(data) == [1, 1, 2, 3, 3, 4, 5, 5]


def test_all_identical() -> None:
    data = [7] * 100
    assert merge_sort(data) == [7] * 100


def test_negative_numbers() -> None:
    data = [0, -5, 10, -3, 7, -10]
    assert merge_sort(data) == [-10, -5, -3, 0, 7, 10]


def test_floats() -> None:
    data = [3.14, 2.71, 1.41, 1.73, 0.58]
    expected = sorted(data)
    assert merge_sort(data) == expected


def test_strings() -> None:
    data = ["banana", "apple", "cherry", "date"]
    assert merge_sort(data) == ["apple", "banana", "cherry", "date"]


def test_mixed_types_via_key() -> None:
    """Different types can be sorted if key normalises them."""
    data = [3, "11", 2, "1", 1, "20"]
    result = merge_sort(data, key=lambda x: int(x))
    assert result == ["1", 1, 2, 3, "11", "20"]


# ── Stability ────────────────────────────────────────────────────────────

def test_stability() -> None:
    """Equal-keyed items preserve their original relative order."""
    pairs = [(2, "a"), (1, "x"), (2, "b"), (1, "y"), (2, "c")]
    result = merge_sort(pairs, key=lambda p: p[0])
    keys = [p[0] for p in result]
    assert keys == [1, 1, 2, 2, 2]
    # Within each key group, original order is preserved
    ones = [(k, v) for (k, v) in result if k == 1]
    twos = [(k, v) for (k, v) in result if k == 2]
    assert ones == [(1, "x"), (1, "y")]
    assert twos == [(2, "a"), (2, "b"), (2, "c")]


# ── Non-mutability ───────────────────────────────────────────────────────

def test_does_not_mutate_original() -> None:
    original = [3, 1, 4, 1, 5, 9]
    snapshot = copy.deepcopy(original)
    merge_sort(original)
    assert original == snapshot, "merge_sort must not mutate the input list"


# ── key parameter ────────────────────────────────────────────────────────

def test_key_abs() -> None:
    data = [-10, 5, -3, 7, -1]
    assert merge_sort(data, key=abs) == [-1, -3, 5, 7, -10]


def test_key_len() -> None:
    data = ["aaaa", "a", "aaa", "aa"]
    assert merge_sort(data, key=len) == ["a", "aa", "aaa", "aaaa"]


def test_key_str_lower() -> None:
    data = ["Banana", "apple", "Cherry", "date"]
    assert merge_sort(data, key=str.lower) == [
        "apple", "Banana", "Cherry", "date"
    ]


def test_key_then_no_key_equivalence() -> None:
    data = [4, 2, 9, 1, 5]
    assert merge_sort(data, key=lambda x: x) == merge_sort(data)


# ── reverse parameter ────────────────────────────────────────────────────

def test_reverse_empty() -> None:
    assert merge_sort([], reverse=True) == []


def test_reverse_single() -> None:
    assert merge_sort([42], reverse=True) == [42]


def test_reverse_basic() -> None:
    data = [3, 1, 4, 1, 5, 9]
    assert merge_sort(data, reverse=True) == [9, 5, 4, 3, 1, 1]


def test_reverse_with_key() -> None:
    data = ["aaa", "a", "aaaa", "aa"]
    assert merge_sort(data, key=len, reverse=True) == [
        "aaaa", "aaa", "aa", "a"
    ]


def test_reverse_matches_sorted() -> None:
    data = [random.randint(-1000, 1000) for _ in range(200)]
    assert merge_sort(data, reverse=True) == sorted(data, reverse=True)


# ── Large lists (performance + correctness) ──────────────────────────────

def test_large_10k() -> None:
    n = 10_000
    data = [random.randint(-1_000_000, 1_000_000) for _ in range(n)]
    expected = sorted(data)
    result = merge_sort(data)
    assert result == expected
    # Verify O(n log n) — should finish well under 5 seconds
    assert len(result) == n


def test_large_100k() -> None:
    """Stress test: 100 000 random integers."""
    n = 100_000
    data = [random.randint(-10_000_000, 10_000_000) for _ in range(n)]
    expected = sorted(data)
    start = time.perf_counter()
    result = merge_sort(data)
    elapsed = time.perf_counter() - start
    assert result == expected
    assert len(result) == n
    assert elapsed < 10.0, f"100k elements took {elapsed:.2f}s — expected < 10s"


def test_large_reverse_sorted() -> None:
    """Algorithm must not degenerate on adversarial input."""
    n = 10_000
    data = list(range(n, 0, -1))  # reverse sorted
    expected = list(range(1, n + 1))
    start = time.perf_counter()
    result = merge_sort(data)
    elapsed = time.perf_counter() - start
    assert result == expected
    assert elapsed < 5.0, f"Reverse 10k took {elapsed:.2f}s"


def test_large_all_duplicates() -> None:
    n = 50_000
    data = [42] * n
    result = merge_sort(data)
    assert result == [42] * n
    assert len(result) == n


# ── type hints are present (manual verifications via inspect) ────────────

def test_merge_sort_has_type_hints() -> None:
    import inspect
    sig = inspect.signature(merge_sort)
    hints = merge_sort.__annotations__
    assert "items" in hints, "Missing type hint for items parameter"
    assert "key" in hints, "Missing type hint for key parameter"
    assert "reverse" in hints, "Missing type hint for reverse parameter"
    assert "return" in hints, "Missing return type hint"


# ── Random fuzz testing ──────────────────────────────────────────────────

def test_random_small() -> None:
    for _ in range(100):
        n = random.randint(0, 50)
        data = [random.randint(-100, 100) for _ in range(n)]
        assert merge_sort(data) == sorted(data)


def test_random_with_key() -> None:
    for _ in range(50):
        n = random.randint(0, 30)
        data = [random.randint(-100, 100) for _ in range(n)]
        # Sort by absolute value, then by value itself
        assert merge_sort(data, key=lambda x: (abs(x), x)) == sorted(
            data, key=lambda x: (abs(x), x)
        )
