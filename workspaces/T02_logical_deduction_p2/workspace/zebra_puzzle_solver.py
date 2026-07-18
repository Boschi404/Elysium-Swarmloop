#!/usr/bin/env python3
"""
Zebra Puzzle (Einstein's Riddle) — Constraint Satisfaction Solver.

Classic puzzle: 5 houses in a row, each with a unique color, nationality,
drink, cigarette, and pet. Using 15 clues, determine who owns the zebra.
"""
import itertools
from typing import Iterator

# ── Domains ──────────────────────────────────────────────────────────────
HOUSES      = [1, 2, 3, 4, 5]          # positions, left = 1
COLORS      = ['Red', 'Green', 'White', 'Yellow', 'Blue']
NATIONALITIES = ['Englishman', 'Swede', 'Dane', 'Norwegian', 'German']
DRINKS      = ['Tea', 'Coffee', 'Milk', 'Beer', 'Water']
CIGARETTES  = ['Pall Mall', 'Dunhill', 'Blends', 'Blue Master', 'Prince']
PETS        = ['Dogs', 'Birds', 'Cats', 'Horses', 'Zebra']

LABELS = ['House', 'Color', 'Nationality', 'Drink', 'Cigarette', 'Pet']

# ── Clue definitions ─────────────────────────────────────────────────────
CLUES = """
1. The Englishman lives in the red house.
2. The Swede keeps dogs.
3. The Dane drinks tea.
4. The green house is immediately left of the white house.
5. The owner of the green house drinks coffee.
6. The person who smokes Pall Mall keeps birds.
7. The owner of the yellow house smokes Dunhill.
8. The man living in the centre house drinks milk.
9. The Norwegian lives in the first house.
10. The man who smokes Blends lives next to the one who keeps cats.
11. The man who keeps horses lives next to the man who smokes Dunhill.
12. The man who smokes Blue Master drinks beer.
13. The German smokes Prince.
14. The Norwegian lives next to the blue house.
15. The man who smokes Blends has a neighbour who drinks water.
"""


def all_unique(values: tuple) -> bool:
    """Return True when all values are distinct (no duplicates)."""
    return len(set(values)) == len(values)


def neighbours(a: int, b: int) -> bool:
    """True when |position_a - position_b| == 1."""
    return abs(a - b) == 1


def is_immediately_left_of(a: int, b: int) -> bool:
    """True when a is immediately to the left of b."""
    return b - a == 1


# ── Candidate generator ──────────────────────────────────────────────────

def solve() -> list[dict]:
    """
    Brute-force over all permutations of each category, filtering with clues.
    Returns every valid assignment (only one should exist for this puzzle).
    """
    solutions = []

    # Pre-compute every permutation of 5 items for each category.
    color_perms = list(itertools.permutations(COLORS))
    nat_perms   = list(itertools.permutations(NATIONALITIES))
    drink_perms = list(itertools.permutations(DRINKS))
    cig_perms   = list(itertools.permutations(CIGARETTES))
    pet_perms   = list(itertools.permutations(PETS))

    total = (len(color_perms) * len(nat_perms))  # ≈ 120 × 120 = 14 400
    checked = 0

    for colors in color_perms:
        for nats in nat_perms:

            # ── Fast pre-filters ─────────────────────────────────────
            # Clue 9: Norwegian in house 1.
            if nats[0] != 'Norwegian':
                continue
            # Clue 14: Norwegian (house 1) next to blue house → house 2 must be blue.
            if colors[1] != 'Blue':
                continue
            # Clue 4: green immediately left of white.
            gi = colors.index('Green')
            wi = colors.index('White')
            if not is_immediately_left_of(gi, wi):
                continue
            # Clue 1: Englishman in red house.
            if nats[colors.index('Red')] != 'Englishman':
                continue
            # Clue 8: centre house (index 2) drinks milk.
            # (deferred to drink loop)

            checked += 1
            if checked % 2000 == 0:
                pass  # progress marker

            for drinks in drink_perms:
                # Clue 8: house 3 (index 2) drinks milk.
                if drinks[2] != 'Milk':
                    continue
                # Clue 5: green house drinks coffee.
                if drinks[gi] != 'Coffee':
                    continue
                # Clue 3: Dane drinks tea.
                di = nats.index('Dane')
                if drinks[di] != 'Tea':
                    continue

                for cigs in cig_perms:
                    # Clue 7: yellow house smokes Dunhill.
                    yi = colors.index('Yellow')
                    if cigs[yi] != 'Dunhill':
                        continue
                    # Clue 13: German smokes Prince.
                    gi_nat = nats.index('German')
                    if cigs[gi_nat] != 'Prince':
                        continue
                    # Clue 12: Blue Master drinks beer.
                    bmi = cigs.index('Blue Master')
                    if drinks[bmi] != 'Beer':
                        continue
                    # Clue 6: Pall Mall keeps birds.
                    pmi = cigs.index('Pall Mall')
                    # deferred to pet loop

                    for pets in pet_perms:
                        # Clue 6: Pall Mall keeps birds.
                        if pets[pmi] != 'Birds':
                            continue
                        # Clue 2: Swede keeps dogs.
                        si = nats.index('Swede')
                        if pets[si] != 'Dogs':
                            continue

                        # Clue 10: Blends next to cats.
                        bi = cigs.index('Blends')
                        ci = pets.index('Cats')
                        if not neighbours(bi, ci):
                            continue

                        # Clue 11: Horses next to Dunhill.
                        hi = pets.index('Horses')
                        if not neighbours(hi, yi):  # yi = yellow house = Dunhill
                            continue

                        # Clue 15: Blends neighbour drinks water.
                        wi_drink = [d for i, d in enumerate(drinks)
                                    if neighbours(i, bi)]
                        if 'Water' not in wi_drink:
                            continue

                        # ── All clues satisfied → record solution ──
                        solution = []
                        for pos in range(5):
                            solution.append({
                                'house': pos + 1,
                                'color': colors[pos],
                                'nationality': nats[pos],
                                'drink': drinks[pos],
                                'cigarette': cigs[pos],
                                'pet': pets[pos],
                            })
                        solutions.append(solution)

    return solutions


def format_solution(solution: list[dict]) -> str:
    """Render a single solution as a formatted table."""
    lines = []
    lines.append(f"\n{'='*70}")
    lines.append("  ZEBRA PUZZLE — SOLUTION")
    lines.append(f"{'='*70}\n")

    header = f"{'House':>6} │ {'Color':<10} │ {'Nationality':<12} │ {'Drink':<10} │ {'Cigarette':<12} │ {'Pet':<8}"
    sep = f"{'─'*6}─┼─{'─'*10}─┼─{'─'*12}─┼─{'─'*10}─┼─{'─'*12}─┼─{'─'*8}"

    lines.append(header)
    lines.append(sep)

    for row in solution:
        lines.append(
            f"{row['house']:>6} │ {row['color']:<10} │ {row['nationality']:<12} │ "
            f"{row['drink']:<10} │ {row['cigarette']:<12} │ {row['pet']:<8}"
        )

    lines.append(f"\n{'─'*70}")

    # Answer
    for row in solution:
        if row['pet'] == 'Zebra':
            lines.append(f"\n  >>> The {row['nationality']} owns the ZEBRA (house {row['house']}). <<<\n")

    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Solving Zebra Puzzle (Einstein's Riddle)...")
    print(f"{'='*70}")
    print(CLUES.strip())

    sols = solve()

    if len(sols) == 0:
        print("\n  ✗ No solution found — check clues.")
    elif len(sols) == 1:
        print(format_solution(sols[0]))
    else:
        print(f"\n  ⚠ Found {len(sols)} solutions (expected 1). Showing first:")
        print(format_solution(sols[0]))
