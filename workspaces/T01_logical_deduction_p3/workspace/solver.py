"""
T01 Logical Deduction — Knights and Knaves Puzzle Solver.

Knights always tell truth, Knaves always lie.
A says: "B is a Knave."
B says: "We are both Knights."
"""

from typing import Literal

Type = Literal["Knight", "Knave"]

STATEMENT_A = "B is a Knave"
STATEMENT_B = "We are both Knights"


def is_knight(person: Type) -> bool:
    return person == "Knight"


def is_knave(person: Type) -> bool:
    return person == "Knave"


def statement_a_true(b: Type) -> bool:
    """A says: 'B is a Knave' — true iff B is actually a Knave."""
    return is_knave(b)


def statement_b_true(a: Type, b: Type) -> bool:
    """B says: 'We are both Knights' — true iff both are Knights."""
    return is_knight(a) and is_knight(b)


def check_consistency(a: Type, b: Type) -> bool:
    """
    Check consistency: each person's statement must match their nature.
    Knight → statement must be true. Knave → statement must be false.
    """
    # A's statement
    a_says_true = statement_a_true(b)
    if is_knight(a) and not a_says_true:
        return False  # Knight cannot lie
    if is_knave(a) and a_says_true:
        return False  # Knave cannot tell truth

    # B's statement
    b_says_true = statement_b_true(a, b)
    if is_knight(b) and not b_says_true:
        return False  # Knight cannot lie
    if is_knave(b) and b_says_true:
        return False  # Knave cannot tell truth

    return True


def solve() -> list[dict]:
    """Test all 4 type assignments and return consistent solutions."""
    types: list[Type] = ["Knight", "Knave"]
    solutions = []

    for a_type in types:
        for b_type in types:
            consistent = check_consistency(a_type, b_type)
            status = "✅ CONSISTENT" if consistent else "❌ CONTRADICTION"
            solutions.append({
                "A": a_type,
                "B": b_type,
                "consistent": consistent,
                "status": status,
                "reason": _contradiction_reason(a_type, b_type, consistent),
            })
    return solutions


def _contradiction_reason(a: Type, b: Type, consistent: bool) -> str:
    if consistent:
        return "All statements match role obligations."
    if a == "Knight" and b == "Knight":
        return "A(Knight) says 'B is Knave' → true, but B is Knight. Knight cannot lie."
    if a == "Knave" and b == "Knight":
        return "B(Knight) says 'both Knights' → false (A is Knave). Knight cannot lie."
    if a == "Knave" and b == "Knave":
        return "A(Knave) says 'B is Knave' → true (B IS Knave). Knave cannot tell truth."
    return "Unknown contradiction."


def main():
    print("=" * 58)
    print("  T01 Logical Deduction — Knights and Knaves Puzzle")
    print("=" * 58)
    print(f'  A says: "{STATEMENT_A}"')
    print(f'  B says: "{STATEMENT_B}"')
    print("=" * 58)
    print()

    solutions = solve()
    for s in solutions:
        print(f"  A={s['A']:>6}  B={s['B']:>6}  →  {s['status']}")
        print(f"    Reason: {s['reason']}")
        print()

    valid = [s for s in solutions if s["consistent"]]
    print("=" * 58)
    print(f"  ✅ Solution found: A={valid[0]['A']}, B={valid[0]['B']}")
    print("=" * 58)


if __name__ == "__main__":
    main()
