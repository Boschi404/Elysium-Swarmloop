"""
Knights and Knaves Puzzle - Solution

Knights always tell the truth.
Knaves always lie.

A says: "B is a Knave."
B says: "We are both Knights."

We enumerate all 4 possible assignments and check for contradictions.
"""

from enum import Enum


class PersonType(Enum):
    KNIGHT = "Knight"
    KNAVE = "Knave"


def is_knight(pt: PersonType) -> bool:
    return pt == PersonType.KNIGHT


def is_knave(pt: PersonType) -> bool:
    return pt == PersonType.KNAVE


def solve() -> dict:
    """
    Enumerate all 4 (A, B) assignments and find the consistent one.
    Returns the solution and the analysis of each case.
    """
    types = [PersonType.KNIGHT, PersonType.KNAVE]
    cases = []
    solution = None

    for a_type in types:
        for b_type in types:
            # A says: "B is a Knave"
            a_statement_true = is_knave(b_type)
            # B says: "We are both Knights"
            b_statement_true = is_knight(a_type) and is_knight(b_type)

            # Knights must speak truth, Knaves must lie
            a_consistent = (
                (is_knight(a_type) and a_statement_true)
                or (is_knave(a_type) and not a_statement_true)
            )
            b_consistent = (
                (is_knight(b_type) and b_statement_true)
                or (is_knave(b_type) and not b_statement_true)
            )

            consistent = a_consistent and b_consistent

            case = {
                "A": a_type.value,
                "B": b_type.value,
                "A_statement": f"B is a {PersonType.KNAVE.value}",
                "A_statement_is_true": a_statement_true,
                "B_statement": "We are both Knights",
                "B_statement_is_true": b_statement_true,
                "A_consistent": a_consistent,
                "B_consistent": b_consistent,
                "consistent": consistent,
            }
            cases.append(case)

            if consistent:
                solution = {
                    "A": a_type.value,
                    "B": b_type.value,
                }

    return {"cases": cases, "solution": solution}


def print_solution():
    result = solve()
    print("=" * 60)
    print("Knights and Knaves Puzzle")
    print("=" * 60)
    print()

    for i, case in enumerate(result["cases"]):
        status = "✅ CONSISTENT" if case["consistent"] else "❌ CONTRADICTION"
        print(f"Case {i + 1}: A = {case['A']:6s}, B = {case['B']:6s}  →  {status}")
        print(f"  A says 'B is a Knave'        → statement is {'TRUE ' if case['A_statement_is_true'] else 'FALSE'}  "
              f"→ A is {'truthful' if case['A_consistent'] else 'LYING'}")
        print(f"  B says 'We are both Knights'  → statement is {'TRUE ' if case['B_statement_is_true'] else 'FALSE'}  "
              f"→ B is {'truthful' if case['B_consistent'] else 'LYING'}")
        print()

    sol = result["solution"]
    print("=" * 60)
    print(f"SOLUTION: A is a {sol['A']}, B is a {sol['B']}.")
    print("=" * 60)


if __name__ == "__main__":
    print_solution()
