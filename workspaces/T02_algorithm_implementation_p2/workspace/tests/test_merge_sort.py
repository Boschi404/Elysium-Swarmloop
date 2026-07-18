"""
Tests for merge_sort.
Covers: empty, single-element, sorted, reverse-sorted, duplicates,
large lists, key parameter, reverse parameter, error cases, stability.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merge_sort import merge_sort


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------

class TestMergeSortBasics:
    def test_empty_list(self):
        assert merge_sort([]) == []

    def test_single_element(self):
        assert merge_sort([42]) == [42]

    def test_two_elements_unsorted(self):
        assert merge_sort([2, 1]) == [1, 2]

    def test_two_elements_sorted(self):
        assert merge_sort([1, 2]) == [1, 2]

    def test_already_sorted(self):
        assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_mixed_order(self):
        assert merge_sort([3, 1, 4, 1, 5, 9, 2, 6, 5]) == [1, 1, 2, 3, 4, 5, 5, 6, 9]

    def test_all_identical(self):
        assert merge_sort([7, 7, 7, 7]) == [7, 7, 7, 7]

    def test_negative_numbers(self):
        assert merge_sort([-3, -1, -2, 0, 4]) == [-3, -2, -1, 0, 4]

    def test_mixed_negatives_positives(self):
        assert merge_sort([0, -1, 5, -10, 3]) == [-10, -1, 0, 3, 5]


# ---------------------------------------------------------------------------
# Large lists
# ---------------------------------------------------------------------------

class TestMergeSortLarge:
    def test_100k_ascending(self):
        n = 100_000
        arr = list(range(n))
        result = merge_sort(arr)
        # Check length and order — avoid materialising full comparison
        assert len(result) == n
        assert result[0] == 0
        assert result[-1] == n - 1
        # Spot-check monotonicity in a few slices
        for i in range(0, n, n // 10):
            if i + 1 < n:
                assert result[i] <= result[i + 1]

    def test_100k_descending(self):
        n = 100_000
        arr = list(range(n - 1, -1, -1))
        result = merge_sort(arr)
        assert len(result) == n
        assert result[0] == 0
        assert result[-1] == n - 1

    def test_100k_random_duplicates(self):
        n = 100_000
        arr = [i // 2 for i in range(n)]  # each value appears twice
        import random
        random.shuffle(arr)
        result = merge_sort(arr)
        assert len(result) == n
        for i in range(n - 1):
            assert result[i] <= result[i + 1]


# ---------------------------------------------------------------------------
# Key parameter
# ---------------------------------------------------------------------------

class TestMergeSortKey:
    def test_key_abs(self):
        assert merge_sort([-4, -1, 3, 2], key=abs) == [-1, 2, 3, -4]

    def test_key_str_len(self):
        assert merge_sort(["bb", "a", "ccc", "dd"], key=len) == ["a", "bb", "dd", "ccc"]

    def test_key_named_attribute(self):
        class Obj:
            def __init__(self, val):
                self.val = val
            def __repr__(self):
                return f"Obj({self.val})"
        objs = [Obj(3), Obj(1), Obj(2)]
        result = merge_sort(objs, key=lambda x: x.val)
        assert [o.val for o in result] == [1, 2, 3]

    def test_key_with_empty_list(self):
        assert merge_sort([], key=abs) == []

    def test_key_with_single(self):
        assert merge_sort([-5], key=abs) == [-5]


# ---------------------------------------------------------------------------
# Reverse parameter
# ---------------------------------------------------------------------------

class TestMergeSortReverse:
    def test_reverse_basic(self):
        assert merge_sort([1, 2, 3, 4, 5], reverse=True) == [5, 4, 3, 2, 1]

    def test_reverse_with_duplicates(self):
        assert merge_sort([3, 1, 4, 1, 5], reverse=True) == [5, 4, 3, 1, 1]

    def test_reverse_empty(self):
        assert merge_sort([], reverse=True) == []

    def test_reverse_single(self):
        assert merge_sort([99], reverse=True) == [99]

    def test_reverse_with_key(self):
        assert merge_sort(["aa", "b", "ccc"], key=len, reverse=True) == ["ccc", "aa", "b"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestMergeSortErrors:
    def test_non_list_raises_typeerror(self):
        try:
            merge_sort("not a list")
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_non_list_tuple(self):
        try:
            merge_sort((1, 2, 3))
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_non_list_generator(self):
        try:
            merge_sort(x for x in [1, 2, 3])
            assert False, "Should have raised TypeError"
        except TypeError:
            pass


# ---------------------------------------------------------------------------
# Stability & non-mutation
# ---------------------------------------------------------------------------

class TestMergeSortStability:
    def test_stable_sort(self):
        """Merge sort is stable: equal elements keep original order."""
        pairs = [(1, "a"), (2, "b"), (1, "c"), (2, "d")]
        result = merge_sort(pairs, key=lambda x: x[0])
        assert result[0] == (1, "a")
        assert result[1] == (1, "c")  # 'a' before 'c' because a appeared first
        assert result[2] == (2, "b")
        assert result[3] == (2, "d")

    def test_does_not_mutate_original(self):
        original = [3, 1, 2]
        copy = original[:]
        result = merge_sort(original)
        assert original == copy  # original unchanged
        assert result == [1, 2, 3]


# ---------------------------------------------------------------------------
# Edge: list of lists, mixed types (comparable)
# ---------------------------------------------------------------------------

class TestMergeSortEdge:
    def test_list_of_tuples(self):
        assert merge_sort([(2, "b"), (1, "a"), (3, "c")]) == [(1, "a"), (2, "b"), (3, "c")]

    def test_float_and_int(self):
        assert merge_sort([3.0, 1.5, 2]) == [1.5, 2, 3.0]

    def test_all_negative_reverse(self):
        assert merge_sort([-5, -1, -3, -2], reverse=True) == [-1, -2, -3, -5]
