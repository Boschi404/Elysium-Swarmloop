"""
Knights and Knaves — Logical Solver

Knights always tell the truth, Knaves always lie.
Given statements from A and B, determine consistent identities.
"""

from typing import Literal, Optional

Person = Literal["Knight", "Knave"]
Statement = str


def is_knight(person: Person) -> bool:
    """A Knight tells truth; a Knave lies."""
    return person == "Knight"


def evaluate(statement: Statement, a: Person, b: Person) -> bool:
    """Evaluate the truth value of a statement about A and B."""
    if statement == "B is a Knave":
        return b == "Knave"
    elif statement == "We are both Knights":
        return a == "Knight" and b == "Knight"
    else:
        raise ValueError(f"Unknown statement: {statement}")


def is_consistent(
    a_type: Person, b_type: Person, a_says: str, b_says: str
) -> bool:
    """
    Check if a (a_type, b_type) assignment is consistent with what they said.
    A Knight's statement must be True; a Knave's statement must be False.
    """
    a_truth = evaluate(a_says, a_type, b_type)
    if is_knight(a_type) != a_truth:
        return False

    b_truth = evaluate(b_says, a_type, b_type)
    if is_knight(b_type) != b_truth:
        return False

    return True


def solve() -> list[dict]:
    """
    Enumerate all 4 possible assignments, return only consistent ones.

    Returns
    -------
    list of dict
        Each dict has keys: a, b, consistent
        consistent=True means this assignment is logically valid.
    """
    results = []
    a_says = "B is a Knave"
    b_says = "We are both Knights"

    for a_type in ("Knight", "Knave"):
        for b_type in ("Knight", "Knave"):
            consistent = is_consistent(a_type, b_type, a_says, b_says)
            results.append(
                {
                    "a": a_type,
                    "b": b_type,
                    "consistent": consistent,
                }
            )

    return results


def print_solution(results: list[dict]) -> None:
    """Pretty-print the truth-table and the solution."""
    print("=" * 50)
    print("Knights and Knaves — Truth Table")
    print("=" * 50)
    print(f"{'#':>2} | {'A':>8} | {'B':>8} | {'Consistent?'}")
    print("-" * 40)
    for i, r in enumerate(results, 1):
        marker = "❌" if not r["consistent"] else "✅"
        print(f"{i:>2} | {r['a']:>8} | {r['b']:>8} | {marker}")

    print()
    solutions = [r for r in results if r["consistent"]]
    if len(solutions) == 1:
        s = solutions[0]
        print(f"✅ Solution: A = {s['a']}, B = {s['b']}")
    elif len(solutions) == 0:
        print("❌ No consistent solution (paradoxical statements)")
    else:
        print(f"⚠️  Multiple solutions ({len(solutions)}): {solutions}")


def solve_knights_and_knaves() -> tuple[Person, Person]:
    """Convenience: returns (a_type, b_type) of the unique solution."""
    results = solve()
    solutions = [r for r in results if r["consistent"]]
    if len(solutions) != 1:
        raise ValueError(
            f"Expected exactly 1 solution, found {len(solutions)}"
        )
    return solutions[0]["a"], solutions[0]["b"]


if __name__ == "__main__":
    results = solve()
    print_solution(results)
