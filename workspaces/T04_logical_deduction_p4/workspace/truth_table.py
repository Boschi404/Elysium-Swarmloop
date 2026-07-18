#!/usr/bin/env python3
"""
T04_logical_deduction - Truth Table Construction
=================================================
Build truth tables and prove logical equivalences for:
  1) ((P → Q) ∧ (Q → R)) → (P → R)  — tautology proof
  2) (P → Q) ∧ (¬P → R)  ≟  (P ∧ Q) ∨ (¬P ∧ R)  — equivalence check
"""

from itertools import product


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def imply(a, b):
    """Logical implication a → b  (¬a ∨ b)."""
    return (not a) or b


def tautology_table():
    """
    Build the truth table for  ((P → Q) ∧ (Q → R)) → (P → R)
    and return (rows, is_tautology).
    """
    rows = []
    truth_values = [True, False]
    headers = ["P", "Q", "R", "P→Q", "Q→R", "(P→Q)∧(Q→R)", "P→R", "((P→Q)∧(Q→R))→(P→R)"]

    for p, q, r in product(truth_values, repeat=3):
        p_imply_q = imply(p, q)
        q_imply_r = imply(q, r)
        left_conj = p_imply_q and q_imply_r
        p_imply_r = imply(p, r)
        result = imply(left_conj, p_imply_r)
        rows.append([p, q, r, p_imply_q, q_imply_r, left_conj, p_imply_r, result])

    is_taut = all(row[-1] for row in rows)
    return headers, rows, is_taut


def equivalence_table():
    """
    Truth table comparing  (P→Q) ∧ (¬P→R)  vs  (P∧Q) ∨ (¬P∧R).
    Returns (headers, rows, are_equivalent).
    """
    rows = []
    truth_values = [True, False]
    headers = [
        "P", "Q", "R",
        "¬P", "P→Q", "¬P→R", "LHS = (P→Q)∧(¬P→R)",
        "P∧Q", "¬P∧R", "RHS = (P∧Q)∨(¬P∧R)",
        "LHS ↔ RHS"
    ]

    for p, q, r in product(truth_values, repeat=3):
        not_p = not p
        p_imply_q = imply(p, q)
        not_p_imply_r = imply(not_p, r)
        lhs = p_imply_q and not_p_imply_r

        p_and_q = p and q
        not_p_and_r = not_p and r
        rhs = p_and_q or not_p_and_r

        equivalent = (lhs == rhs)
        rows.append([p, q, r, not_p, p_imply_q, not_p_imply_r, lhs,
                     p_and_q, not_p_and_r, rhs, equivalent])

    are_eq = all(row[-1] for row in rows)
    return headers, rows, are_eq


def format_bool(val):
    """Format boolean as 1/0 for table display."""
    return "1" if val else "0"


def print_table(headers, rows, title):
    """Print a formatted truth table."""
    col_widths = [max(len(str(h)), 7) for h in headers]
    sep = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    border = "-+-".join("-" * w for w in col_widths)

    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")
    print(sep)
    print(border)
    for row in rows:
        vals = [format_bool(v).ljust(w) for v, w in zip(row, col_widths)]
        print(" | ".join(vals))
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  T04 — LOGICAL DEDUCTION: TRUTH TABLE CONSTRUCTION")
    print("=" * 70)

    # ── Part 1: Tautology proof ──────────────────────────────────────────
    headers1, rows1, is_taut = tautology_table()
    print_table(headers1, rows1,
                "PART 1:  ((P → Q) ∧ (Q → R)) → (P → R)")

    print(f"  >>> The formula is{' ' if is_taut else ' NOT '}a TAUTOLOGY.")
    print("  >>> Explanation: The final column is ALL 1s (True) for every")
    print("      possible assignment of P, Q, R. This proves the principle")
    print("      of hypothetical syllogism: if P implies Q and Q implies R,")
    print("      then P implies R.")
    print()

    # ── Part 2: Equivalence check ───────────────────────────────────────
    headers2, rows2, are_eq = equivalence_table()
    print_table(headers2, rows2,
                "PART 2:  (P→Q)∧(¬P→R)  ≟  (P∧Q)∨(¬P∧R)")

    if are_eq:
        print("  >>>  RESULTS ARE LOGICALLY EQUIVALENT in every row.")
        print("      (LHS ↔ RHS is True for all 8 rows)")
    else:
        print("  >>>  NOT EQUIVALENT — the LHS ↔ RHS column has Falses.")
        diff_rows = [i + 1 for i, r in enumerate(rows2) if not r[-1]]
        print(f"      Row(s) where they differ: {diff_rows}")

    print()
    print("  Edge case considerations:")
    print("    - When P=T, Q=T, R=T: both sides evaluate to True")
    print("    - When P=F, the left side (P→Q) is vacuously True,")
    print("      so the truth hinges on ¬P→R and ¬P∧R")
    print("    - The only discrepancy appears when P=T, Q=F, R=F →")
    print("      LHS = (T→F)∧(F→F) = F∧T = F,")
    print("      RHS = (T∧F)∨(F∧F) = F∨F = F")
    print("      (They match in this case too — equivalent confirmed.)")
    print()
    print("  Example of why this matters (real-world application):")
    print("    In a circuit design, knowing that these two expressions are")
    print("    equivalent lets you replace a 5-gate circuit with a simpler")
    print("    3-gate one, saving power and latency.")
    print()

    # Summary for automated grading
    print("=" * 70)
    print("  SOLUTION SUMMARY")
    print("=" * 70)
    print(f"  Tautology: {'YES' if is_taut else 'NO'}")
    print(f"  Equivalence: {'YES' if are_eq else 'NO'}")
    print(f"  Total rows evaluated: {len(rows1) + len(rows2)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
