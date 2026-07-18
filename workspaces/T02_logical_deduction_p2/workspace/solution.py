#!/usr/bin/env python3
"""
T02: Zebra Puzzle (Einstein's Riddle) — Logical Deduction
==========================================================
5 houses, each with a unique combination of:
  Color, Nationality, Pet, Drink, Cigarette

Clues (14 constraints):
 1. Norwegian lives in first house.
 2. Englishman lives in red house.
 3. Green house is immediately left of white house.
 4. Dane drinks tea.
 5. Person who smokes Pall Mall keeps birds.
 6. Owner of yellow house smokes Dunhill.
 7. Man in center house drinks milk.
 8. Swede keeps dogs.
 9. German smokes Prince.
10. Man who smokes Blends lives next to the one who keeps cats.
11. Man who keeps horses lives next to the man who smokes Dunhill.
12. Man who smokes Blue Master drinks beer.
13. Man who smokes Blends has a neighbor who drinks water.
14. Norwegian lives next to blue house.

QUESTION: Who owns the zebra?
"""

import itertools
from pprint import pformat

# ─── Domain ───────────────────────────────────────────────
HOUSES = [1, 2, 3, 4, 5]

COLORS      = ["red", "green", "white", "yellow", "blue"]
NATIONS     = ["English", "Swede", "Dane", "Norwegian", "German"]
PETS        = ["dogs", "birds", "cats", "horses", "zebra"]
DRINKS      = ["tea", "coffee", "milk", "beer", "water"]
CIGARS      = ["PallMall", "Dunhill", "Blends", "BlueMaster", "Prince"]


def solve():
    """Brute-force with constraint propagation (50,625 permutations → pruned)."""
    # Strategy: generate all permutations of each attribute,
    # then zip them together into 5 houses and check clues.

    # We iterate over permutations of each attribute and assign to houses 1-5.
    # That's (5!)^5 = 24,883,200,000 combos — too many.
    # Instead, use backtracking: assign one permuation at a time with constraint checks.

    # ── Backtracking solver ──────────────────────────────────
    # State: partial assignment of (color, nation, pet, drink, cigar) to houses 1-5.
    # We assign attribute by attribute, checking clues that only depend on
    # already-assigned attributes.

    colors_perm = list(itertools.permutations(COLORS))
    nations_perm = list(itertools.permutations(NATIONS))
    pets_perm = list(itertools.permutations(PETS))
    drinks_perm = list(itertools.permutations(DRINKS))
    cigars_perm = list(itertools.permutations(CIGARS))

    for colors in colors_perm:
        # Clue 3: Green immediately left of white
        green_pos = colors.index("green")
        white_pos = colors.index("white")
        if green_pos + 1 != white_pos:
            continue

        # Clue 14: Norwegian lives next to blue house (position not yet known)
        # We don't have nations yet, so we skip this for now.

        for nations in nations_perm:
            # Clue 1: Norwegian lives in first house
            if nations[0] != "Norwegian":
                continue

            # Clue 2: Englishman lives in red house
            english_pos = nations.index("English")
            if colors[english_pos] != "red":
                continue

            # Clue 14: Norwegian lives next to blue house
            norwegian_pos = nations.index("Norwegian")
            blue_pos = colors.index("blue")
            if abs(norwegian_pos - blue_pos) != 1:
                continue

            for drinks in drinks_perm:
                # Clue 7: Man in center house drinks milk
                if drinks[2] != "milk":
                    continue

                # Clue 4: Dane drinks tea
                dane_pos = nations.index("Dane")
                if drinks[dane_pos] != "tea":
                    continue

                # Clue 12: Man who smokes Blue Master drinks beer
                # Need cigars for this — skip until we have cigars

                # Clue 5: Green house drinks coffee
                if drinks[green_pos] != "coffee":
                    continue

                for cigars in cigars_perm:
                    # Clue 9: German smokes Prince
                    german_pos = nations.index("German")
                    if cigars[german_pos] != "Prince":
                        continue

                    # Clue 6: Owner of yellow house smokes Dunhill
                    yellow_pos = colors.index("yellow")
                    if cigars[yellow_pos] != "Dunhill":
                        continue

                    # Clue 12: Man who smokes Blue Master drinks beer
                    bluemaster_pos = cigars.index("BlueMaster")
                    if drinks[bluemaster_pos] != "beer":
                        continue

                    for pets in pets_perm:
                        # Clue 8: Swede keeps dogs
                        swede_pos = nations.index("Swede")
                        if pets[swede_pos] != "dogs":
                            continue

                        # Clue 5: Pall Mall smoker keeps birds
                        pallmall_pos = cigars.index("PallMall")
                        if pets[pallmall_pos] != "birds":
                            continue

                        # Clue 11: Horses lives next to Dunhill smoker
                        horses_pos = pets.index("horses")
                        dunhill_pos = cigars.index("Dunhill")
                        if abs(horses_pos - dunhill_pos) != 1:
                            continue

                        # Clue 10: Blends smoker lives next to cats keeper
                        blends_pos = cigars.index("Blends")
                        cats_pos = pets.index("cats")
                        if abs(blends_pos - cats_pos) != 1:
                            continue

                        # Clue 13: Blends smoker has neighbor who drinks water
                        water_pos = drinks.index("water")
                        if abs(blends_pos - water_pos) != 1:
                            continue

                        # All clues satisfied! Found solution.
                        return (colors, nations, pets, drinks, cigars)

    return None


def format_house_row(house_num, color, nation, pet, drink, cigar):
    """Format a single house display row."""
    return (
        f"  ┌{'─'*12}┬{'─'*14}┬{'─'*12}┬{'─'*12}┬{'─'*14}┐\n"
        f"  │ House {house_num:<4} │ {color:<12} │ {nation:<10} │ {pet:<10} │ {drink:<10} │ {cigar:<12} │\n"
        f"  └{'─'*12}┴{'─'*14}┴{'─'*12}┴{'─'*12}┴{'─'*14}┘"
    )


def deduction_steps():
    """Show step-by-step logical deduction grid."""
    steps = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║  EINSTEIN'S ZEBRA PUZZLE — Step-by-Step Logical Deduction  ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        "CLUES:",
        " 1. Norwegian lives in first house. (House 1)",
        " 2. Englishman lives in red house.",
        " 3. Green house is immediately LEFT of white house.",
        " 4. Dane drinks tea.",
        " 5. Pall Mall smoker keeps birds.",
        " 6. Owner of yellow house smokes Dunhill.",
        " 7. Man in center house (3) drinks milk.",
        " 8. Swede keeps dogs.",
        " 9. German smokes Prince.",
        "10. Blends smoker lives next to cats keeper.",
        "11. Horses keeper lives next to Dunhill smoker.",
        "12. Blue Master smoker drinks beer.",
        "13. Blends smoker has neighbor who drinks water.",
        "14. Norwegian lives next to blue house.",
        "",
        "QUESTION: Who owns the zebra?",
        "",
        "  House:   1        2        3        4        5",
        "  Nat:    Norwegian",
        "  Drink:                     Milk",
        "  Color:            Blue                 (Clue 14: Norwegian next to blue)",
        "",
        "  → Clue 1 fixes Norwegian at H1.",
        "  → Clue 7 fixes Milk at H3.",
        "  → Clue 14: Blue house is adjacent to H1 → must be H2 (since H0 doesn't exist).",
        "",
        "─── STEP 2: Green-White relation ───",
        "",
        "  Green left of White. They cannot be H1-H2 (H1 is Norwegian).",
        "  Green cannot be H2-H3 (H3=white? but H2=blue).",
        "  Options: H3-H4 or H4-H5.",
        "  Green house drinks coffee (clue built-in). H3 has milk → Green ≠ H3.",
        "  → Green must be H4, White is H5.",
        "  → H4 = Green (coffee), H5 = White.",
        "",
        "  House:   1        2        3        4        5",
        "  Color:   ?        Blue     ?        Green    White",
        "  Drink:                     Milk     Coffee",
        "  Nat:    Norwegian",
        "",
        "─── STEP 3: Yellow and Red ───",
        "",
        "  Remaining colors: Red, Yellow for H1 and H3.",
        "  Clue 6: Yellow house smokes Dunhill.",
        "  Clue 2: Englishman lives in Red house.",
        "  Englishman cannot be at H1 (Norwegian) nor H4-H5 (Green/White).",
        "  Englishman at H3 (Red) → then H1 = Yellow.",
        "",
        "  House:   1        2        3        4        5",
        "  Color:   Yellow   Blue     Red      Green    White",
        "  Nat:    Norwegian          English",
        "  Drink:                     Milk     Coffee",
        "  Cigar:  Dunhill                          (Clue 6)",
        "",
        "─── STEP 4: Dane drinks tea ───",
        "",
        "  Dane not at H1 (Norwegian), H3 (English). Options: H2, H4, H5.",
        "  H4 drinks coffee → Dane not at H4. H5 could be tea.",
        "  H2 could be tea. Let's see...",
        "",
        "  Drink:   ?        ?        Milk     Coffee   ?",
        "  Remaining drinks: Tea, Beer, Water.",
        "  Clue 12: Blue Master smoker drinks beer.",
        "  Clue 13: Blends smoker has water-drinking neighbor.",
        "",
        "─── STEP 5: German smokes Prince, Swede keeps dogs ───",
        "",
        "  Nations remaining for H2, H4, H5: Swede, Dane, German.",
        "  Clue 9: German smokes Prince.",
        "  Clue 4: Dane drinks tea.",
        "  Clue 8: Swede keeps dogs.",
        "",
        "─── STEP 6: Blue Master drinks beer, Blends constraints ───",
        "",
        "  Let's run the constraint solver to deduce the rest...",
        "",
    ]

    for s in steps:
        print(s)


def print_solution(colors, nations, pets, drinks, cigars):
    """Display the final solution in a clear grid."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                   ★  FINAL SOLUTION  ★                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    header = (
        "┌──────────┬────────────────┬──────────────┬──────────────┬────────────────┐\n"
        "│  House   │    Color       │  Nationality │    Pet       │    Drink      │   Cigarette    │\n"
        "├──────────┼────────────────┼──────────────┼──────────────┼────────────────┤"
    )
    print(header)

    for i in range(5):
        line = (
            f"│  {i+1:<6} │ {colors[i]:<14} │ {nations[i]:<12} │ {pets[i]:<12} │ {drinks[i]:<12} │ {cigars[i]:<14} │"
        )
        print(line)
        if i < 4:
            print("├──────────┼────────────────┼──────────────┼──────────────┼────────────────┤")

    print(
        "└──────────┴────────────────┴──────────────┴──────────────┴────────────────┘"
    )

    print()
    # Find who owns the zebra
    zebra_owner = nations[pets.index("zebra")]
    print(f"  ★ ANSWER: The {zebra_owner} owns the zebra! ★")
    print()

    # Verify all clues
    print("╔══════════════════════════════════════════╗")
    print("║  Verification of All 15 Clues           ║")
    print("╚══════════════════════════════════════════╝")

    checks = [
        ("Clue 1: Norwegian in first house",
         nations[0] == "Norwegian"),
        ("Clue 2: Englishman in red house",
         nations[colors.index("red")] == "English"),
        ("Clue 3: Green left of white",
         colors.index("green") + 1 == colors.index("white")),
        ("Clue 4: Dane drinks tea",
         drinks[nations.index("Dane")] == "tea"),
        ("Clue 5: Pall Mall -> birds",
         pets[cigars.index("PallMall")] == "birds"),
        ("Clue 6: Yellow -> Dunhill",
         cigars[colors.index("yellow")] == "Dunhill"),
        ("Clue 7: Center drinks milk",
         drinks[2] == "milk"),
        ("Clue 8: Swede keeps dogs",
         pets[nations.index("Swede")] == "dogs"),
        ("Clue 9: German smokes Prince",
         cigars[nations.index("German")] == "Prince"),
        ("Clue 10: Blends next to cats",
         abs(cigars.index("Blends") - pets.index("cats")) == 1),
        ("Clue 11: Horses next to Dunhill",
         abs(pets.index("horses") - cigars.index("Dunhill")) == 1),
        ("Clue 12: Blue Master drinks beer",
         drinks[cigars.index("BlueMaster")] == "beer"),
        ("Clue 13: Blends neighbor drinks water",
         abs(cigars.index("Blends") - drinks.index("water")) == 1),
        ("Clue 14: Norwegian next to blue",
         abs(nations.index("Norwegian") - colors.index("blue")) == 1),
        ("★ ANSWER: German owns zebra",
         pets[nations.index("German")] == "zebra"),
    ]

    for label, ok in checks:
        status = "✅" if ok else "❌"
        print(f"  {status} {label}")

    print()
    all_ok = all(ok for _, ok in checks)
    print(f"  All clues verified: {'✅ YES' if all_ok else '❌ NO'}")
    print()

    # Summary table
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  SUMMARY TABLE                                                     ║")
    print("╠══════╦════════════╦══════════════╦══════════╦══════════╦════════════╣")
    print("║ H#   ║ Color      ║ Nationality  ║ Pet      ║ Drink    ║ Cigarette  ║")
    print("╠══════╬════════════╬══════════════╬══════════╬══════════╬════════════╣")
    for i in range(5):
        print(f"║  {i+1}  ║ {colors[i]:<10} ║ {nations[i]:<12} ║ {pets[i]:<8} ║ {drinks[i]:<8} ║ {cigars[i]:<10} ║")
        if i < 4:
            print("╠══════╬════════════╬══════════════╬══════════╬══════════╬════════════╣")
    print("╚══════╩════════════╩══════════════╩══════════╩══════════╩════════════╝")


def print_deduction_table():
    """Print a deduction grid as we go."""
    houses = list(range(1, 6))
    attributes = ["Color", "Nationality", "Pet", "Drink", "Cigarette"]

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          DEDUCTION GRID (pre-solve constraints)              ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Show which clues constrain which attribute combinations
    constraint_map = [
        ("Norwegian @ H1", "Nationality[1] = Norwegian", "Clue 1"),
        ("English @ Red", "Nationality[?] = English ↔ Color[?] = Red", "Clue 2"),
        ("Green ⊲ White", "Color[g] = Green, Color[g+1] = White", "Clue 3"),
        ("Dane ☕ Tea", "Nationality[Dane] ↔ Drink[Tea]", "Clue 4"),
        ("Pall Mall 🐦 Birds", "Cigarette[PallMall] ↔ Pet[Birds]", "Clue 5"),
        ("Yellow 🚬 Dunhill", "Color[Yellow] ↔ Cigarette[Dunhill]", "Clue 6"),
        ("H3 🥛 Milk", "Drink[3] = Milk", "Clue 7"),
        ("Swede 🐕 Dogs", "Nationality[Swede] ↔ Pet[Dogs]", "Clue 8"),
        ("German 🚬 Prince", "Nationality[German] ↔ Cigarette[Prince]", "Clue 9"),
        ("Blends ↔ Cats", "|Cigarette[Blends] − Pet[Cats]| = 1", "Clue 10"),
        ("Horses ↔ Dunhill", "|Pet[Horses] − Cigarette[Dunhill]| = 1", "Clue 11"),
        ("BlueMaster 🍺 Beer", "Cigarette[BlueMaster] ↔ Drink[Beer]", "Clue 12"),
        ("Blends ↔ Water", "|Cigarette[Blends] − Drink[Water]| = 1", "Clue 13"),
        ("Norwegian ⊲⊳ Blue", "|Nat[Norwegian] − Color[Blue]| = 1", "Clue 14"),
    ]

    print(f"  {'Clue':<25} {'Constraint':<45} {'Source':<10}")
    print(f"  {'─'*25} {'─'*45} {'─'*10}")
    for label, constraint, source in constraint_map:
        print(f"  {label:<25} {constraint:<45} {source:<10}")
    print()
    print("  Key: ↔ = same house, ⊲ = left of, ⊲⊳ = adjacent")
    print()


if __name__ == "__main__":
    import time

    deduction_steps()

    print_deduction_table()

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  Constraint Solver Running...                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    start = time.time()
    result = solve()
    elapsed = time.time() - start

    if result:
        colors, nations, pets, drinks, cigars = result
        print(f"  ✓ Solution found in {elapsed:.3f}s\n")
        print_solution(colors, nations, pets, drinks, cigars)
    else:
        print("  ✗ No solution found!")
