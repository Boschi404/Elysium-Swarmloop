#!/usr/bin/env python3
"""
Zebra Puzzle (Einstein's Riddle) — Logical Deduction Solver
============================================================

Solves the classic 5-house logic puzzle using constraint propagation.
Determines step by step who owns the zebra.

Clues used (15 total):
  1. Norwegian lives in first house
  2. Englishman lives in red house
  3. Green house is immediately left of white house
  4. Dane drinks tea
  5. Pall Mall smoker keeps birds
  6. Yellow house smokes Dunhill
  7. Center house (position 3) drinks milk
  8. Norwegian lives next to blue house
  9. German smokes Prince
  10. Blend smoker lives next to cat keeper
  11. Horse keeper lives next to Dunhill smoker
  12. Swede keeps dogs
  13. Blue Master smoker drinks beer
  14. Blend smoker has a neighbor who drinks water
  15. Green house drinks coffee
"""

from itertools import permutations
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────
#  Category domain values
# ──────────────────────────────────────────────────────────────
COLORS = ("Red", "Green", "White", "Yellow", "Blue")
NATIONS = ("Norwegian", "Englishman", "Dane", "German", "Swede")
DRINKS = ("Tea", "Milk", "Water", "Beer", "Coffee")
SMOKES = ("Pall Mall", "Dunhill", "Prince", "Blend", "Blue Master")
PETS = ("Birds", "Dogs", "Cats", "Horses", "Zebra")

POSITIONS = (1, 2, 3, 4, 5)  # house positions left → right


def solve() -> Optional[List[Dict[str, str]]]:
    """
    Brute-force with pruning: assign all permutations of
    colors, nations, drinks, smokes and pets to 5 houses
    and verify against all 15 clues.

    Returns a list of 5 house dicts indexed by position,
    or None if no solution found.
    """
    for colors in permutations(COLORS):
        # Clue 3: green immediately left of white
        green_idx = colors.index("Green")
        if green_idx == 4:  # green cannot be last
            continue
        if colors[green_idx + 1] != "White":
            continue

        for nations in permutations(NATIONS):
            # Clue 1: Norwegian in house 1
            if nations[0] != "Norwegian":
                continue
            # Clue 2: Englishman in red house
            if nations[colors.index("Red")] != "Englishman":
                continue
            # Clue 8: Norwegian (house 1) lives next to blue house
            if colors[1] != "Blue":  # house 2 must be blue
                continue

            for drinks in permutations(DRINKS):
                # Clue 7: center house (pos 3) drinks milk
                if drinks[2] != "Milk":
                    continue
                # Clue 4: Dane drinks tea
                if drinks[nations.index("Dane")] != "Tea":
                    continue
                # Clue 15: green house drinks coffee
                if drinks[green_idx] != "Coffee":
                    continue

                for smokes in permutations(SMOKES):
                    # Clue 6: yellow house smokes Dunhill
                    if smokes[colors.index("Yellow")] != "Dunhill":
                        continue
                    # Clue 9: German smokes Prince
                    if smokes[nations.index("German")] != "Prince":
                        continue
                    # Clue 13: Blue Master smoker drinks beer
                    bm_idx = smokes.index("Blue Master")
                    if drinks[bm_idx] != "Beer":
                        continue

                    for pets in permutations(PETS):
                        # Clue 5: Pall Mall smoker keeps birds
                        if pets[smokes.index("Pall Mall")] != "Birds":
                            continue
                        # Clue 12: Swede keeps dogs
                        if pets[nations.index("Swede")] != "Dogs":
                            continue
                        # Clue 10: Blend smoker lives next to cat keeper
                        blend_idx = smokes.index("Blend")
                        cat_idx = pets.index("Cats")
                        if abs(blend_idx - cat_idx) != 1:
                            continue
                        # Clue 11: horse keeper lives next to Dunhill smoker
                        horse_idx = pets.index("Horses")
                        dunhill_idx = smokes.index("Dunhill")
                        if abs(horse_idx - dunhill_idx) != 1:
                            continue
                        # Clue 14: Blend smoker has neighbor who drinks water
                        water_idx = drinks.index("Water")
                        if abs(blend_idx - water_idx) != 1:
                            continue

                        # All clues satisfied — build result
                        houses = []
                        for pos in POSITIONS:
                            idx = pos - 1
                            houses.append({
                                "position": pos,
                                "color": colors[idx],
                                "nationality": nations[idx],
                                "drink": drinks[idx],
                                "smoke": smokes[idx],
                                "pet": pets[idx],
                            })
                        return houses

    return None


def deduction_grid(houses: List[Dict[str, str]]) -> str:
    """Render the solution as an ASCII deduction grid."""
    lines = []
    lines.append("=" * 72)
    lines.append("                  ZEBRA PUZZLE — DEDUCTION GRID")
    lines.append("=" * 72)
    lines.append("")
    header = f"{'House':>8} {'Color':>10} {'Nationality':>14} {'Drink':>10} {'Smoke':>14} {'Pet':>10}"
    lines.append(header)
    lines.append("-" * len(header))
    for h in houses:
        lines.append(
            f"{h['position']:>8} {h['color']:>10} {h['nationality']:>14} "
            f"{h['drink']:>10} {h['smoke']:>14} {h['pet']:>10}"
        )
    lines.append("")
    return "\n".join(lines)


def step_by_step(houses: List[Dict[str, str]]) -> str:
    """
    Return a human-readable step-by-step deduction narrative,
    showing each clue and the inference drawn.
    """
    lines = []
    lines.append("=" * 72)
    lines.append("            STEP-BY-STEP LOGICAL DEDUCTION")
    lines.append("=" * 72)
    lines.append("")

    steps = [
        (
            "1",
            "Norwegian in house 1",
            f"House 1 → Norwegian. House 2 → Blue (clue 8: Norwegian lives next to blue).",
        ),
        (
            "2",
            "Milk in house 3",
            "Center house (position 3) drinks milk (clue 7).",
        ),
        (
            "3",
            "Green left of white → pos 4-5",
            "Clue 3: green is immediately left of white. Possibilities: (3,4) or (4,5). "
            "Pos 3 has milk; clue 15 says green drinks coffee → (3,4) impossible. "
            "Green=4, White=5, and green drinks coffee.",
        ),
        (
            "4",
            "Red house = Englishman → pos 3",
            "Red cannot be 2 (blue), 4 (green), or 5 (white). Not 1 (Norwegian). "
            "Red = 3 → Englishman in house 3.",
        ),
        (
            "5",
            "Yellow = house 1 → smokes Dunhill",
            "Only color left for house 1 is Yellow. Clue 6: Yellow smokes Dunhill → house 1 smokes Dunhill.",
        ),
        (
            "6",
            "Horses next to Dunhill → house 2 has horses",
            "Clue 11: horse keeper lives next to Dunhill smoker. Dunhill is house 1 → house 2 has horses.",
        ),
        (
            "7",
            "Dane drinks tea → house 2 (by elimination)",
            "Clue 4: Dane drinks tea. Positions without drink: 1, 2, 5. "
            "Pos 4 has coffee, pos 3 has milk. Tea cannot be in pos 1 (Norwegian) — no conflict, "
            "but pos 2 works best with Danish = tea. Try Dane in pos 2.",
        ),
        (
            "8",
            "Blue Master drinks beer → house 5",
            "Clue 13: Blue Master smoker drinks beer. Beer cannot be pos 3 (milk) or pos 4 (coffee). "
            "If beer were pos 1, Blue Master would be pos 1, but pos 1 smokes Dunhill. "
            "So beer = pos 5, Blue Master = pos 5.",
        ),
        (
            "9",
            "German smokes Prince → house 4",
            "Clue 9: German smokes Prince. Available positions: 4 or 5. "
            "Pos 5 smokes Blue Master → German cannot be pos 5. German = pos 4, Prince = pos 4.",
        ),
        (
            "10",
            "Pall Mall → house 3 (with birds)",
            "Clue 5: Pall Mall smoker keeps birds. Available: pos 2 or 3. "
            "Pos 2 has horses, Pall Mall keeps birds → pos 3 = Pall Mall + birds.",
        ),
        (
            "11",
            "Blend → house 2",
            "Only cigarette left for pos 2 is Blend.",
        ),
        (
            "12",
            "Swede keeps dogs → house 5",
            "Clue 12: Swede keeps dogs. Only pos 5 is unassigned. "
            "House 5 = Swede + Blue Master + Beer + Dogs.",
        ),
        (
            "13",
            "Water → house 1",
            "Only drink left for pos 1 is Water.",
        ),
        (
            "14",
            "Blend neighbor drinks water → house 1 ✓",
            "Clue 14: Blend smoker (pos 2) has neighbor who drinks water (pos 1) ✓",
        ),
        (
            "15",
            "Blend neighbor keeps cats → house 1 has cats",
            "Clue 10: Blend smoker (pos 2) lives next to cat keeper. "
            "Pos 3 has birds, so cat keeper = pos 1. Zebra → pos 4.",
        ),
        (
            "★",
            "CONCLUSION",
            "The GERMAN in house 4 (Green) owns the ZEBRA.",
        ),
    ]

    lines.append(
        "Clue inventory: 1) Norwegian#1  2) Englishman=Red  3) Green<White  "
        "4) Dane=Tea  5) Pall Mall=Birds\n"
        "6) Yellow=Dunhill  7) Milk#3  8) Norwegian~Blue  9) German=Prince  "
        "10) Blend~Cats\n"
        "11) Horses~Dunhill  12) Swede=Dogs  13) Blue Master=Beer  "
        "14) Blend~Water  15) Green=Coffee\n"
    )

    for num, title, text in steps:
        lines.append(f"  [{num:>2}]  {title}")
        lines.append(f"        {text}")
        lines.append("")

    # Final grid
    lines.append(deduction_grid(houses))
    lines.append("")
    lines.append("Answer: The German owns the zebra.")
    lines.append("")

    return "\n".join(lines)


def main():
    result = solve()
    if result is None:
        print("ERROR: No solution found!")
        return

    print(step_by_step(result))

    # Verify all clues
    print("=" * 72)
    print("                    CLAUSE VERIFICATION")
    print("=" * 72)
    print("")
    checks = verify_all(result)
    for desc, ok in checks:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {status}  {desc}")
    print("")
    print(f"  → All {sum(1 for _, ok in checks if ok)}/{len(checks)} clues verified.")
    print("")


def verify_all(houses: List[Dict[str, str]]) -> List[Tuple[str, bool]]:
    """Test every clue against the solved grid."""
    def by_pos(pos: int) -> Dict[str, str]:
        return houses[pos - 1]

    def find(key: str, value: str) -> Dict[str, str]:
        return next(h for h in houses if h[key] == value)

    checks = []

    # 1 — Norwegian in house 1
    checks.append(("Norwegian lives in house 1", by_pos(1)["nationality"] == "Norwegian"))
    # 2 — Englishman in red
    checks.append(("Englishman in red house", find("color", "Red")["nationality"] == "Englishman"))
    # 3 — Green left of white
    g = find("color", "Green")
    w = find("color", "White")
    checks.append(("Green immediately left of White", g["position"] + 1 == w["position"]))
    # 4 — Dane drinks tea
    checks.append(("Dane drinks tea", find("nationality", "Dane")["drink"] == "Tea"))
    # 5 — Pall Mall keeps birds
    checks.append(("Pall Mall smoker keeps birds", find("smoke", "Pall Mall")["pet"] == "Birds"))
    # 6 — Yellow smokes Dunhill
    checks.append(("Yellow house smokes Dunhill", find("color", "Yellow")["smoke"] == "Dunhill"))
    # 7 — Center drinks milk
    checks.append(("Center house drinks milk", by_pos(3)["drink"] == "Milk"))
    # 8 — Norwegian next to blue
    n_pos = find("nationality", "Norwegian")["position"]
    b_pos = find("color", "Blue")["position"]
    checks.append(("Norwegian lives next to blue house", abs(n_pos - b_pos) == 1))
    # 9 — German smokes Prince
    checks.append(("German smokes Prince", find("nationality", "German")["smoke"] == "Prince"))
    # 10 — Blend next to cats
    blend_pos = find("smoke", "Blend")["position"]
    cat_pos = find("pet", "Cats")["position"]
    checks.append(("Blend smoker lives next to cat keeper", abs(blend_pos - cat_pos) == 1))
    # 11 — Horses next to Dunhill
    horse_pos = find("pet", "Horses")["position"]
    dunhill_pos = find("smoke", "Dunhill")["position"]
    checks.append(("Horse keeper lives next to Dunhill smoker", abs(horse_pos - dunhill_pos) == 1))
    # 12 — Swede keeps dogs
    checks.append(("Swede keeps dogs", find("nationality", "Swede")["pet"] == "Dogs"))
    # 13 — Blue Master drinks beer
    checks.append(("Blue Master smoker drinks beer", find("smoke", "Blue Master")["drink"] == "Beer"))
    # 14 — Blend neighbor drinks water
    checks.append(("Blend smoker's neighbor drinks water", abs(blend_pos - find("drink", "Water")["position"]) == 1))
    # 15 — Green drinks coffee
    checks.append(("Green house drinks coffee", find("color", "Green")["drink"] == "Coffee"))

    # Uniqueness checks
    cats = [h["pet"] for h in houses]
    checks.append(("All 5 pets distinct", len(set(cats)) == 5))
    checks.append(("Zebra is assigned to someone", any(h["pet"] == "Zebra" for h in houses)))

    return checks


if __name__ == "__main__":
    main()
