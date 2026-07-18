"""
T03: Logical Deduction — Syllogism Validity Check
=================================================
Evaluates the syllogism:
    All programmers are logical.
    Some logical people are mathematicians.
    Therefore, some programmers are mathematicians.
"""

def check_syllogism() -> dict:
    """
    Models the syllogism as sets and verifies each premise and conclusion.
    Returns a dict with the validity verdict and explanation.
    """
    # Universe of individuals
    universe = {"Alice", "Bob", "Charlie", "Dave", "Ella"}

    # Sets
    programmers = {"Alice", "Bob"}
    logical = {"Alice", "Bob", "Charlie", "Dave"}  # Ella is illogical
    mathematicians = {"Charlie", "Dave"}

    results = {}

    # Premise 1: All programmers are logical (P ⊆ L)
    p1 = programmers.issubset(logical)
    results["premise1"] = {
        "statement": "All programmers are logical (P ⊆ L)",
        "sets": {"P": sorted(programmers), "L": sorted(logical)},
        "result": p1,
        "detail": f"{sorted(programmers)} ⊆ {sorted(logical)} → {p1}"
    }

    # Premise 2: Some logical people are mathematicians (L ∩ M ≠ ∅)
    intersection_lm = logical & mathematicians
    p2 = len(intersection_lm) > 0
    results["premise2"] = {
        "statement": "Some logical people are mathematicians (L ∩ M ≠ ∅)",
        "sets": {"L": sorted(logical), "M": sorted(mathematicians)},
        "result": p2,
        "intersection": sorted(intersection_lm),
        "detail": f"L ∩ M = {sorted(intersection_lm)} → {p2}"
    }

    # Conclusion: Some programmers are mathematicians (P ∩ M ≠ ∅)
    intersection_pm = programmers & mathematicians
    conclusion = len(intersection_pm) > 0
    results["conclusion"] = {
        "statement": "Some programmers are mathematicians (P ∩ M ≠ ∅)",
        "sets": {"P": sorted(programmers), "M": sorted(mathematicians)},
        "result": conclusion,
        "intersection": sorted(intersection_pm),
        "detail": f"P ∩ M = {sorted(intersection_pm)} → {conclusion}"
    }

    # Verdict
    premises_true = p1 and p2
    results["valid"] = premises_true and conclusion

    results["verdict"] = (
        "INVALID — Fallacy of the Undistributed Middle\n"
        "Both premises are true, but the conclusion is false. "
        "The logical-mathematician overlap lies entirely outside the programmer set."
    )

    return results


def counterexample_text() -> str:
    """Returns a textual counterexample using set notation."""
    return """Counterexample (Set Notation):

  P = {Alice, Bob}           ← programmers
  L = {Alice, Bob, Charlie, Dave}  ← logical people
  M = {Charlie, Dave}        ← mathematicians

  Check 1: P ⊆ L?  {Alice, Bob} ⊆ {Alice, Bob, Charlie, Dave}  ✅
  Check 2: L ∩ M ≠ ∅?  {Charlie, Dave} ≠ ∅  ✅
  Check 3: P ∩ M ≠ ∅?  ∅  ❌

  Premises hold, conclusion fails → INVALID
"""


def venn_diagram_text() -> str:
    """ASCII Venn diagram showing the counterexample."""
    return """
┌──────────────────────────────┐
│          LOGICAL (L)         │
│  ┌────────┐    ┌────────┐   │
│  │  P (P) │    │ M (M)  │   │
│  │        │    │        │   │
│  │ Alice  │    │Charlie │   │
│  │ Bob    │    │ Dave   │   │
│  │        │    │        │   │
│  └────────┘    └────────┘   │
│                              │
│  Outside: Ella (illogical)   │
└──────────────────────────────┘

  P ∩ M = ∅  →  No programmer is a mathematician
"""


if __name__ == "__main__":
    import json

    result = check_syllogism()
    print("=" * 60)
    print("SYLLOGISM: All programmers are logical.")
    print("           Some logical people are mathematicians.")
    print("           Therefore, some programmers are mathematicians.")
    print("=" * 60)
    print()
    print(json.dumps(result, indent=2))
    print()
    print(counterexample_text())
    print(venn_diagram_text())
    print(f"Final verdict: {'✅ VALID' if result['valid'] else '❌ INVALID'}")
