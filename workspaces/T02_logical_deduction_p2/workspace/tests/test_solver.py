"""
Tests for the Zebra Puzzle solver.
Verifies the CSP solver finds the correct unique solution.
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from workspace.solver import solve_zebra, verify_solution, NATIONALITIES, PETS, DRINKS


def test_solution_exists():
    """Solver must find a solution."""
    solution = solve_zebra()
    assert solution is not None, "CSP solver returned None"
    assert len(solution) == 5, f"Expected 5 houses, got {len(solution)}"


def test_solution_all_houses_filled():
    """Each house must have all 5 attributes assigned."""
    solution = solve_zebra()
    for i, house in enumerate(solution):
        missing = [k for k in ("color", "nationality", "pet", "drink", "smoke")
                   if k not in house or house[k] is None]
        assert not missing, f"House {i+1} missing: {missing}"


def test_solution_unique_per_category():
    """Each value in every category appears exactly once."""
    solution = solve_zebra()
    for cat, all_vals in [
        ("color", ["Red", "Green", "White", "Yellow", "Blue"]),
        ("nationality", ["Englishman", "Spaniard", "Dane", "Norwegian", "German"]),
        ("pet", ["Dog", "Snails", "Fox", "Horse", "Zebra"]),
        ("drink", ["Tea", "Coffee", "Milk", "Beer", "Water"]),
        ("smoke", ["OldGold", "Kools", "Chesterfields", "LuckyStrike", "Parliaments"]),
    ]:
        found = [house[cat] for house in solution]
        assert sorted(found) == sorted(all_vals), \
            f"Category '{cat}': expected {sorted(all_vals)}, got {sorted(found)}"


def test_zebra_is_owned():
    """Someone must own the zebra."""
    solution = solve_zebra()
    owners = [h for h in solution if h.get("pet") == "Zebra"]
    assert len(owners) == 1, f"Expected 1 zebra owner, found {len(owners)}"
    assert owners[0]["nationality"] == "German", \
        f"Expected German to own zebra, got {owners[0]['nationality']}"


def test_water_drinker():
    """Someone must drink water."""
    solution = solve_zebra()
    drinkers = [h for h in solution if h.get("drink") == "Water"]
    assert len(drinkers) == 1, f"Expected 1 water drinker, found {len(drinkers)}"
    assert drinkers[0]["nationality"] == "Norwegian", \
        f"Expected Norwegian to drink water, got {drinkers[0]['nationality']}"


def test_all_fifteen_clues_pass():
    """All 15 clues must be satisfied."""
    solution = solve_zebra()
    passed, total, _ = verify_solution(solution)
    assert passed == total, f"Only {passed}/{total} clues satisfied"
    assert total == 15, f"Expected 15 clues, got {total}"


def test_unique_solution():
    """The puzzle must have exactly one solution."""
    # Run solver multiple times — each run should give the same result
    s1 = solve_zebra()
    s2 = solve_zebra()
    s3 = solve_zebra()

    def canonical(houses):
        return tuple(
            tuple(sorted(h.items())) for h in houses
        )

    assert canonical(s1) == canonical(s2), "Solutions differ between runs"
    assert canonical(s2) == canonical(s3), "Solutions differ between runs"


def test_clue_1_englishman_red():
    """Clue 1: Englishman lives in red house."""
    solution = solve_zebra()
    e = [i for i, h in enumerate(solution) if h["nationality"] == "Englishman"][0]
    r = [i for i, h in enumerate(solution) if h["color"] == "Red"][0]
    assert e == r, f"Englishman in house {e+1}, Red in house {r+1}"


def test_clue_2_spaniard_dog():
    """Clue 2: Spaniard owns dog."""
    solution = solve_zebra()
    s = [i for i, h in enumerate(solution) if h["nationality"] == "Spaniard"][0]
    d = [i for i, h in enumerate(solution) if h["pet"] == "Dog"][0]
    assert s == d


def test_clue_3_coffee_green():
    """Clue 3: Coffee in green house."""
    solution = solve_zebra()
    c = [i for i, h in enumerate(solution) if h["drink"] == "Coffee"][0]
    g = [i for i, h in enumerate(solution) if h["color"] == "Green"][0]
    assert c == g


def test_clue_4_dane_tea():
    """Clue 4: Dane drinks tea."""
    solution = solve_zebra()
    d = [i for i, h in enumerate(solution) if h["nationality"] == "Dane"][0]
    t = [i for i, h in enumerate(solution) if h["drink"] == "Tea"][0]
    assert d == t


def test_clue_5_green_right_of_white():
    """Clue 5: Green immediately right of White."""
    solution = solve_zebra()
    g = [i for i, h in enumerate(solution) if h["color"] == "Green"][0]
    w = [i for i, h in enumerate(solution) if h["color"] == "White"][0]
    assert g == w + 1, f"Green at {g+1}, White at {w+1} (not adjacent right)"


def test_clue_6_oldgold_snails():
    """Clue 6: Old Gold smoker owns snails."""
    solution = solve_zebra()
    o = [i for i, h in enumerate(solution) if h["smoke"] == "OldGold"][0]
    s = [i for i, h in enumerate(solution) if h["pet"] == "Snails"][0]
    assert o == s


def test_clue_7_kools_yellow():
    """Clue 7: Kools in yellow house."""
    solution = solve_zebra()
    k = [i for i, h in enumerate(solution) if h["smoke"] == "Kools"][0]
    y = [i for i, h in enumerate(solution) if h["color"] == "Yellow"][0]
    assert k == y


def test_clue_8_milk_middle():
    """Clue 8: Milk in house 3 (0-indexed: 2)."""
    solution = solve_zebra()
    m = [i for i, h in enumerate(solution) if h["drink"] == "Milk"][0]
    assert m == 2, f"Milk at house {m+1}, expected house 3"


def test_clue_9_norwegian_first():
    """Clue 9: Norwegian in house 1 (0-indexed: 0)."""
    solution = solve_zebra()
    n = [i for i, h in enumerate(solution) if h["nationality"] == "Norwegian"][0]
    assert n == 0, f"Norwegian at house {n+1}, expected house 1"


def test_clue_10_chesterfields_next_fox():
    """Clue 10: Chesterfields next to fox."""
    solution = solve_zebra()
    c = [i for i, h in enumerate(solution) if h["smoke"] == "Chesterfields"][0]
    f = [i for i, h in enumerate(solution) if h["pet"] == "Fox"][0]
    assert abs(c - f) == 1


def test_clue_11_kools_next_horse():
    """Clue 11: Kools next to horse."""
    solution = solve_zebra()
    k = [i for i, h in enumerate(solution) if h["smoke"] == "Kools"][0]
    h = [i for i, h in enumerate(solution) if h["pet"] == "Horse"][0]
    assert abs(k - h) == 1


def test_clue_12_luckystrike_beer():
    """Clue 12: Lucky Strike drinks beer."""
    solution = solve_zebra()
    l = [i for i, h in enumerate(solution) if h["smoke"] == "LuckyStrike"][0]
    b = [i for i, h in enumerate(solution) if h["drink"] == "Beer"][0]
    assert l == b


def test_clue_13_german_parliaments():
    """Clue 13: German smokes Parliaments."""
    solution = solve_zebra()
    g = [i for i, h in enumerate(solution) if h["nationality"] == "German"][0]
    p = [i for i, h in enumerate(solution) if h["smoke"] == "Parliaments"][0]
    assert g == p


def test_clue_14_norwegian_next_blue():
    """Clue 14: Norwegian next to blue house."""
    solution = solve_zebra()
    n = [i for i, h in enumerate(solution) if h["nationality"] == "Norwegian"][0]
    b = [i for i, h in enumerate(solution) if h["color"] == "Blue"][0]
    assert abs(n - b) == 1


def test_clue_15_chesterfields_water():
    """Clue 15: Chesterfields neighbor drinks water."""
    solution = solve_zebra()
    c = [i for i, h in enumerate(solution) if h["smoke"] == "Chesterfields"][0]
    w = [i for i, h in enumerate(solution) if h["drink"] == "Water"][0]
    assert abs(c - w) == 1
