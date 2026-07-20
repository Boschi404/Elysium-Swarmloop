#!/usr/bin/env python3
"""
Zebra Puzzle (Einstein's Riddle) — Constraint Satisfaction Solver
with step-by-step deduction grid.

PUZZLE (15 clues, classic "Life International" 1962 version):
  Five houses in a row, each with a unique color, nationality,
  pet, drink, and cigarette brand.
"""

import itertools
import sys


# ──────────────────────────────────────────────────────────────────────
# CATEGORIES AND VALUES
# ──────────────────────────────────────────────────────────────────────

COLORS = ["Red", "Green", "White", "Yellow", "Blue"]
NATIONALITIES = ["Englishman", "Spaniard", "Dane", "Norwegian", "German"]
PETS = ["Dog", "Snails", "Fox", "Horse", "Zebra"]
DRINKS = ["Tea", "Coffee", "Milk", "Beer", "Water"]
SMOKES = ["OldGold", "Kools", "Chesterfields", "LuckyStrike", "Parliaments"]

ALL_CATS = {
    "color": COLORS,
    "nationality": NATIONALITIES,
    "pet": PETS,
    "drink": DRINKS,
    "smoke": SMOKES,
}


# ──────────────────────────────────────────────────────────────────────
# CONSTRAINT SOLVER (recursive backtracking with forward checking)
# ──────────────────────────────────────────────────────────────────────

class CSP:
    """Generic Constraint Satisfaction Problem solver."""

    def __init__(self):
        # Variables: each is (category, value) and domain is {0,1,2,3,4}
        self.vars = {}
        self.domains = {}
        self.constraints = []
        self.var_list = []

    def add_var(self, name, domain):
        self.vars[name] = None
        self.domains[name] = set(domain)
        self.var_list.append(name)

    def add_constraint(self, fn, relevant_vars):
        """fn takes dict of {var: value} and returns bool."""
        self.constraints.append((fn, relevant_vars))

    def is_consistent(self, assignments):
        for fn, relevant_vars in self.constraints:
            relevant_assign = {v: assignments[v] for v in relevant_vars if v in assignments}
            if len(relevant_assign) == len(relevant_vars):  # all relevant vars assigned
                if not fn(relevant_assign):
                    return False
        return True

    def solve(self, assignments=None):
        if assignments is None:
            assignments = {}
        if len(assignments) == len(self.var_list):
            return assignments

        # Pick unassigned variable
        for var in self.var_list:
            if var not in assignments:
                break

        for val in sorted(self.domains[var]):
            assignments[var] = val
            if self.is_consistent(assignments):
                result = self.solve(assignments)
                if result is not None:
                    return result
            del assignments[var]

        return None


def solve_zebra():
    """Build and solve the CSP for the Zebra Puzzle."""
    csp = CSP()

    # Create variables: (category, value) for each value in each category
    # Value means the house index (0-4) where this attribute is found
    # Example: ("color", "Red") = 2 means red house is at position 2

    for cat_name, values in ALL_CATS.items():
        for val in values:
            csp.add_var((cat_name, val), list(range(5)))

    # ── Uniqueness constraints ──
    # Each value in a category maps to a different house
    for cat_name, values in ALL_CATS.items():
        for v1, v2 in itertools.combinations(values, 2):
            csp.add_constraint(
                lambda a, c=cat_name, v1=v1, v2=v2: a[(c, v1)] != a[(c, v2)],
                [(cat_name, v1), (cat_name, v2)]
            )

    # Also each house has exactly one value per category
    # (implied by the uniqueness + 5 values per 5 houses)

    # ── Clue 1: Englishman in red house ──
    csp.add_constraint(
        lambda a: a[("nationality", "Englishman")] == a[("color", "Red")],
        [("nationality", "Englishman"), ("color", "Red")]
    )

    # ── Clue 2: Spaniard owns dog ──
    csp.add_constraint(
        lambda a: a[("nationality", "Spaniard")] == a[("pet", "Dog")],
        [("nationality", "Spaniard"), ("pet", "Dog")]
    )

    # ── Clue 3: Coffee in green house ──
    csp.add_constraint(
        lambda a: a[("drink", "Coffee")] == a[("color", "Green")],
        [("drink", "Coffee"), ("color", "Green")]
    )

    # ── Clue 4: Dane drinks tea ──
    csp.add_constraint(
        lambda a: a[("nationality", "Dane")] == a[("drink", "Tea")],
        [("nationality", "Dane"), ("drink", "Tea")]
    )

    # ── Clue 5: Green house is immediately to the right of White ──
    csp.add_constraint(
        lambda a: a[("color", "Green")] == a[("color", "White")] + 1,
        [("color", "Green"), ("color", "White")]
    )

    # ── Clue 6: Old Gold smoker owns snails ──
    csp.add_constraint(
        lambda a: a[("smoke", "OldGold")] == a[("pet", "Snails")],
        [("smoke", "OldGold"), ("pet", "Snails")]
    )

    # ── Clue 7: Kools in yellow house ──
    csp.add_constraint(
        lambda a: a[("smoke", "Kools")] == a[("color", "Yellow")],
        [("smoke", "Kools"), ("color", "Yellow")]
    )

    # ── Clue 8: Milk in middle house (index 2, 0‑based) ──
    csp.add_constraint(
        lambda a: a[("drink", "Milk")] == 2,
        [("drink", "Milk")]
    )

    # ── Clue 9: Norwegian in first house (index 0) ──
    csp.add_constraint(
        lambda a: a[("nationality", "Norwegian")] == 0,
        [("nationality", "Norwegian")]
    )

    # ── Clue 10: Chesterfields next to fox ──
    csp.add_constraint(
        lambda a: abs(a[("smoke", "Chesterfields")] - a[("pet", "Fox")]) == 1,
        [("smoke", "Chesterfields"), ("pet", "Fox")]
    )

    # ── Clue 11: Kools next to horse ──
    csp.add_constraint(
        lambda a: abs(a[("smoke", "Kools")] - a[("pet", "Horse")]) == 1,
        [("smoke", "Kools"), ("pet", "Horse")]
    )

    # ── Clue 12: Lucky Strike smoker drinks beer ──
    csp.add_constraint(
        lambda a: a[("smoke", "LuckyStrike")] == a[("drink", "Beer")],
        [("smoke", "LuckyStrike"), ("drink", "Beer")]
    )

    # ── Clue 13: German smokes Parliaments ──
    csp.add_constraint(
        lambda a: a[("nationality", "German")] == a[("smoke", "Parliaments")],
        [("nationality", "German"), ("smoke", "Parliaments")]
    )

    # ── Clue 14: Norwegian next to blue house ──
    csp.add_constraint(
        lambda a: abs(a[("nationality", "Norwegian")] - a[("color", "Blue")]) == 1,
        [("nationality", "Norwegian"), ("color", "Blue")]
    )

    # ── Clue 15: Chesterfields neighbor drinks water ──
    csp.add_constraint(
        lambda a: abs(a[("smoke", "Chesterfields")] - a[("drink", "Water")]) == 1,
        [("smoke", "Chesterfields"), ("drink", "Water")]
    )

    # ── Solve ──
    solution = csp.solve()
    if solution is None:
        return None

    # Convert to house-based view
    houses = [{} for _ in range(5)]
    for (cat, val), house_idx in solution.items():
        houses[house_idx][cat] = val

    return houses


# ──────────────────────────────────────────────────────────────────────
# DEDUCTION GRID GENERATOR (step-by-step logical deduction)
# ──────────────────────────────────────────────────────────────────────

def deduction_table():
    """Return step-by-step deduction text."""
    steps = r"""
════════════════════════════════════════════════════════════════════════
  STEP-BY-STEP DEDUCTION (Manual Reasoning Reconstruction)
════════════════════════════════════════════════════════════════════════

  We number houses 1 (leftmost) to 5 (rightmost).

  ────────────────────────────────────────────────────────────────
  STEP 1 — Clue 9: Norwegian lives in house 1.
  ────────────────────────────────────────────────────────────────
    House 1 = Norwegian.

  ────────────────────────────────────────────────────────────────
  STEP 2 — Clue 8: Milk is drunk in the middle house (house 3).
  ────────────────────────────────────────────────────────────────
    House 3 = Milk.

  ────────────────────────────────────────────────────────────────
  STEP 3 — Clue 14: Norwegian lives next to the blue house.
  ────────────────────────────────────────────────────────────────
    Norwegian is in house 1. The only adjacent house is house 2.
    Therefore: House 2 = Blue.

  ────────────────────────────────────────────────────────────────
  STEP 4 — Clue 2: Englishman lives in red house.
           Clue 5: Green is immediately to the right of White.
  ────────────────────────────────────────────────────────────────
    Green must be immediately right of White. Possible pairs:
      (White=1,Green=2), (2,3), (3,4), (4,5)
    But house 1 is not yet assigned a color, house 2 = Blue.
    
    If Green=2, White=1 → impossible (house 2 is Blue).
    If Green=3, White=2 → impossible (house 2 is Blue).
    If Green=4, White=3 → possible.
    If Green=5, White=4 → possible.
    
    Let's check both cases:
    CASE A: White=3, Green=4 → remaining colors: Red, Yellow for houses 1,5.
            Red must be where Englishman is.
            If Red=5, Englishman=5, Yellow=1.
            If Red=1, Englishman=1, Yellow=5 → but house 1 is Norwegian (contradiction).
            So: Yellow=1, Red=5, Englishman=5.
    CASE B: White=4, Green=5 → remaining colors: Red, Yellow for houses 1,3.
            If Red=1, Englishman=1 → but house 1 is Norwegian (contradiction).
            So: Red=3, Englishman=3, Yellow=1.
    
    Both seem possible so far. Continue to narrow down.

  ────────────────────────────────────────────────────────────────
  STEP 5 — Clue 7: Kools are smoked in the yellow house.
  ────────────────────────────────────────────────────────────────
    CASE A: Yellow=1, Kools=1. CASE B: Yellow=1, Kools=1.
    Both cases agree: House 1 = Yellow, House 1 = Kools.

  ────────────────────────────────────────────────────────────────
  STEP 6 — Clue 11: Kools (house 1) smoked next to where horse is kept.
  ────────────────────────────────────────────────────────────────
    Kools are in house 1, so horse must be next door → House 2 = Horse.

  ────────────────────────────────────────────────────────────────
  STEP 7 — Clue 3: Coffee is drunk in the green house.
  ────────────────────────────────────────────────────────────────
    CASE A: Green=4, Coffee=4.
    CASE B: Green=5, Coffee=5.

  ────────────────────────────────────────────────────────────────
  STEP 8 — Clue 4: Dane drinks tea.
  ────────────────────────────────────────────────────────────────
    The Dane cannot be in house 1 (Norwegian) or house 3 (Englishman in CASE B).
    Possible houses for Dane: 2, 4 (or 5 in CASE A where Englishman=5).

    CASE A: Nations: 1=Norwegian, 5=Englishman. Dane can be 2,3,4.
    CASE B: Nations: 1=Norwegian, 3=Englishman. Dane can be 2,4,5.

  ────────────────────────────────────────────────────────────────
  STEP 9 — Clue 13: German smokes Parliaments.
  ────────────────────────────────────────────────────────────────
    CASE A: Remaining nations for houses 2,3,4: Spaniard, Dane, German.
    CASE B: Remaining nations for houses 2,4,5: Spaniard, Dane, German.

  ────────────────────────────────────────────────────────────────
  ... (further deductions continue, narrowing possibilities) ...

  ────────────────────────────────────────────────────────────────
  FINAL: Only CASE B leads to a consistent solution.
════════════════════════════════════════════════════════════════════════
"""
    return steps.strip()


# ──────────────────────────────────────────────────────────────────────
# SOLUTION FORMATTER
# ──────────────────────────────────────────────────────────────────────

def format_solution(solution):
    """Format the final solution as a table."""
    lines = []
    lines.append("=" * 72)
    lines.append("  ZEBRA PUZZLE — FINAL SOLUTION")
    lines.append("=" * 72)

    headers = ["House", "Color", "Nationality", "Drink", "Smoke", "Pet"]
    col_w = 14
    header_line = "".join(f"{h:>{col_w}}" for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))

    for i in range(5):
        row = [f"{i + 1}"]
        for cat in ["color", "nationality", "drink", "smoke", "pet"]:
            row.append(solution[i].get(cat, "?"))
        lines.append("".join(f"{v:>{col_w}}" for v in row))

    lines.append("=" * 72)
    return "\n".join(lines)


def verify_solution(solution):
    """Verify the solution against all 15 clues. Return (pass_count, total, details)."""
    def h(nat=None, color=None, pet=None, drink=None, smoke=None):
        for i in range(5):
            match = True
            if nat and solution[i].get("nationality") != nat:
                match = False
            if color and solution[i].get("color") != color:
                match = False
            if pet and solution[i].get("pet") != pet:
                match = False
            if drink and solution[i].get("drink") != drink:
                match = False
            if smoke and solution[i].get("smoke") != smoke:
                match = False
            if match:
                return i
        return None

    details = []

    checks = [
        (1, "Englishman in red",
         lambda: (h(nat="Englishman"), h(color="Red")),
         lambda e, r: e == r),
        (2, "Spaniard owns dog",
         lambda: (h(nat="Spaniard"), h(pet="Dog")),
         lambda s, d: s == d),
        (3, "Coffee in green",
         lambda: (h(drink="Coffee"), h(color="Green")),
         lambda c, g: c == g),
        (4, "Dane drinks tea",
         lambda: (h(nat="Dane"), h(drink="Tea")),
         lambda d, t: d == t),
        (5, "Green right of White (adjacent)",
         lambda: (h(color="Green"), h(color="White")),
         lambda g, w: g == w + 1),
        (6, "Old Gold owns snails",
         lambda: (h(smoke="OldGold"), h(pet="Snails")),
         lambda o, s: o == s),
        (7, "Kools in yellow",
         lambda: (h(smoke="Kools"), h(color="Yellow")),
         lambda k, y: k == y),
        (8, "Milk in middle (house 3)",
         lambda: (h(drink="Milk"),),
         lambda m: m == 2),
        (9, "Norwegian first (house 1)",
         lambda: (h(nat="Norwegian"),),
         lambda n: n == 0),
        (10, "Chesterfields next to fox",
         lambda: (h(smoke="Chesterfields"), h(pet="Fox")),
         lambda c, f: abs(c - f) == 1),
        (11, "Kools next to horse",
         lambda: (h(smoke="Kools"), h(pet="Horse")),
         lambda k, h_: abs(k - h_) == 1),
        (12, "Lucky Strike drinks beer",
         lambda: (h(smoke="LuckyStrike"), h(drink="Beer")),
         lambda l, b: l == b),
        (13, "German smokes Parliaments",
         lambda: (h(nat="German"), h(smoke="Parliaments")),
         lambda g, p: g == p),
        (14, "Norwegian next to blue",
         lambda: (h(nat="Norwegian"), h(color="Blue")),
         lambda n, b: abs(n - b) == 1),
        (15, "Chesterfields neighbor drinks water",
         lambda: (h(smoke="Chesterfields"), h(drink="Water")),
         lambda c, w: abs(c - w) == 1),
    ]

    passed = 0
    for num, desc, getter, checker in checks:
        vals = getter()
        result = checker(*vals)
        val_names = ", ".join(
            f"{solution[v].get('nationality', solution[v].get('color', ''))} in house {v + 1}"
            if v is not None else "?"
            for v in (vals if isinstance(vals, tuple) else (vals,))
        )
        icon = "✅" if result else "❌"
        details.append(f"      {icon} Clue {num}: {desc} — {val_names}")
        if result:
            passed += 1

    return passed, len(checks), details


# ──────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  ZEBRA PUZZLE (Einstein's Riddle) — Constraint Satisfaction Solver")
    print("=" * 72)
    print()
    print("  CATEGORIES:")
    print(f"    Colors:       {', '.join(COLORS)}")
    print(f"    Nationalities:{', '.join(NATIONALITIES)}")
    print(f"    Pets:         {', '.join(PETS)}")
    print(f"    Drinks:       {', '.join(DRINKS)}")
    print(f"    Smokes:       {', '.join(SMOKES)}")
    print()
    print("  CLUES:")
    clue_texts = [
        " 1. Englishman lives in the red house.",
        " 2. Spaniard owns the dog.",
        " 3. Coffee is drunk in the green house.",
        " 4. Dane drinks tea.",
        " 5. Green house is immediately to the right of the white house.",
        " 6. Old Gold smoker owns snails.",
        " 7. Kools are smoked in the yellow house.",
        " 8. Milk is drunk in the middle house (house 3).",
        " 9. Norwegian lives in the first house (house 1).",
        "10. Chesterfields smoker lives next to the man with the fox.",
        "11. Kools are smoked next to the house where the horse is kept.",
        "12. Lucky Strike smoker drinks beer.",
        "13. German smokes Parliaments.",
        "14. Norwegian lives next to the blue house.",
        "15. Chesterfields smoker has a neighbor who drinks water.",
    ]
    for t in clue_texts:
        print(f"    {t}")
    print()
    print("  QUESTION: Who owns the zebra?")
    print()

    # ── Solve ──
    print("  Running CSP solver...")
    solution = solve_zebra()

    if solution is None:
        print("  ❌ No solution found. Check constraints.")
        return

    # ── Print solution ──
    print()
    print(format_solution(solution))
    print()

    # ── Answer ──
    for i in range(5):
        if solution[i].get("pet") == "Zebra":
            print(f"  ▶ The {solution[i]['nationality']} owns the zebra in house {i+1}!")
        if solution[i].get("drink") == "Water":
            print(f"  ▶ The {solution[i]['nationality']} drinks water in house {i+1}!")
    print()

    # ── Step-by-step deduction ──
    print(deduction_table())
    print()

    # ── Verification ──
    print("=" * 72)
    print("  VERIFICATION AGAINST ALL 15 CLUES:")
    print("=" * 72)
    passed, total, details = verify_solution(solution)
    for d in details:
        print(d)
    print()
    print(f"  Result: {passed}/{total} clues satisfied {'✅' if passed == total else '❌'}")
    if passed == total:
        print()
        print("=" * 72)
        owner = solution[[i['pet'] for i in solution].index('Zebra')]['nationality']
        water_drinker = solution[[i['drink'] for i in solution].index('Water')]['nationality']
        print(f"  ✓ The {owner} owns the zebra!")
        print(f"  ✓ The {water_drinker} drinks water!")
        print("=" * 72)
    print()


if __name__ == "__main__":
    main()
