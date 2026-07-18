#!/usr/bin/env python3
"""
Knights and Knaves Puzzle — T01_logical_deduction

On an island:
  - Knights ALWAYS tell the truth
  - Knaves ALWAYS lie

Statements:
  A says: "B is a Knave."
  B says: "We are both Knights."

We enumerate all 4 possible assignments and eliminate contradictions.
"""

from typing import Literal

Person = Literal["Knight", "Knave"]


def is_knight(p: Person) -> bool:
    return p == "Knight"


def is_knave(p: Person) -> bool:
    return p == "Knave"


def statement_a(p_a: Person, p_b: Person) -> bool:
    """A says: 'B is a Knave'.
    If A is Knight → B must be Knave (truth).
    If A is Knave → B must NOT be Knave (lie)."""
    if is_knight(p_a):
        return is_knave(p_b)   # truth-teller: statement must be true
    else:
        return not is_knave(p_b)  # liar: statement must be false


def statement_b(p_a: Person, p_b: Person) -> bool:
    """B says: 'We are both Knights'.
    If B is Knight → both must be Knights (truth).
    If B is Knave → it must NOT be true that both are Knights (lie)."""
    both_knights = is_knight(p_a) and is_knight(p_b)
    if is_knight(p_b):
        return both_knights   # truth-teller: statement must be true
    else:
        return not both_knights  # liar: statement must be false


def solve() -> list[tuple[Person, Person, str]]:
    """Enumerate all 4 assignments and return consistent ones."""
    people: list[Person] = ["Knight", "Knave"]
    solutions = []

    for a in people:
        for b in people:
            a_consistent = statement_a(a, b)
            b_consistent = statement_b(a, b)
            if a_consistent and b_consistent:
                solutions.append((a, b, f"A={a}, B={b} — consistent"))
            else:
                print(f"  ❌ A={a}, B={b} — INCONSISTENT "
                      f"(A stmt correct? {a_consistent}, "
                      f"B stmt correct? {b_consistent})")

    return solutions


def main():
    print("=" * 58)
    print("  Knights & Knaves — T01_logical_deduction")
    print("=" * 58)
    print()
    print("Given:")
    print("  A says: 'B is a Knave.'")
    print("  B says: 'We are both Knights.'")
    print()

    cases = [
        ("Case 1: A=Knight, B=Knight", "Knight", "Knight"),
        ("Case 2: A=Knight, B=Knave",  "Knight", "Knave"),
        ("Case 3: A=Knave,  B=Knight", "Knave",  "Knight"),
        ("Case 4: A=Knave,  B=Knave",  "Knave",  "Knave"),
    ]

    for label, a_val, b_val in cases:
        a_ok = statement_a(a_val, b_val)
        b_ok = statement_b(a_val, b_val)
        ok = "✅ CONSISTENT" if (a_ok and b_ok) else "❌ INCONSISTENT"
        print(f"  {label}")
        print(f"    A says 'B is Knave' → {'truth' if a_ok else 'lie'}   "
              f"B says 'both Knights' → {'truth' if b_ok else 'lie'}")
        print(f"    → {ok}")
        print()

    solutions = solve()

    print("-" * 58)
    if len(solutions) == 1:
        a, b, desc = solutions[0]
        print(f"\n✅ UNIQUE SOLUTION: {desc}")
        print(f"\nExplanation:")
        print(f"  A ({a}) says 'B is a Knave' — that is "
              f"{'TRUE' if a == 'Knight' else 'FALSE'}.")
        print(f"  B ({b}) says 'We are both Knights' — that is "
              f"{'TRUE' if b == 'Knight' else 'FALSE'}.")
        print(f"  No other assignment avoids contradiction.")
    elif len(solutions) == 0:
        print("\n❌ No consistent solution exists — puzzle is paradoxical!")
    else:
        print(f"\n⚠️  {len(solutions)} consistent solutions found:")
        for a, b, desc in solutions:
            print(f"  • {desc}")


if __name__ == "__main__":
    main()
