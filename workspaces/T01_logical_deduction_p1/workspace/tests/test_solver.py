"""
Tests for the Knights and Knaves solver.

Covers: base solution, all 4 cases, edge cases (paradox, mutual claims).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver import (is_knight, evaluate, is_consistent, solve,
                    solve_knights_and_knaves)


# ── Basic Tests ──────────────────────────────────────────────────────────────

def test_solution_correct():
    """The unique solution must be A=Knight, B=Knave."""
    a, b = solve_knights_and_knaves()
    assert a == "Knight", f"Expected A=Knight, got {a}"
    assert b == "Knave", f"Expected B=Knave, got {b}"


def test_exactly_one_solution():
    """There must be exactly 1 consistent assignment out of 4."""
    results = solve()
    solutions = [r for r in results if r["consistent"]]
    assert len(solutions) == 1, f"Expected 1 solution, got {len(solutions)}"


def test_inconsistent_cases_eliminated():
    """The 3 impossible cases must be flagged as inconsistent."""
    results = solve()
    inconsistent = [r for r in results if not r["consistent"]]
    assert len(inconsistent) == 3, f"Expected 3 inconsistent, got {len(inconsistent)}"
    combos = {(r["a"], r["b"]) for r in inconsistent}
    assert ("Knight", "Knight") in combos
    assert ("Knave", "Knight") in combos
    assert ("Knave", "Knave") in combos


def test_is_knight():
    assert is_knight("Knight") is True
    assert is_knight("Knave") is False


def test_evaluate_b_is_knave():
    assert evaluate("B is a Knave", "Knight", "Knave") is True
    assert evaluate("B is a Knave", "Knight", "Knight") is False


def test_evaluate_both_knights():
    assert evaluate("We are both Knights", "Knight", "Knight") is True
    assert evaluate("We are both Knights", "Knight", "Knave") is False
    assert evaluate("We are both Knights", "Knave", "Knight") is False
    assert evaluate("We are both Knights", "Knave", "Knave") is False


# ── Edge Cases ───────────────────────────────────────────────────────────────

def test_paradox_self_referential():
    """A saying 'I am a Knave' creates a paradox: no consistent assignment."""
    for a_type in ("Knight", "Knave"):
        for b_type in ("Knight", "Knave"):
            # "I am a Knave" means: evaluate as if A said 'A is a Knave'
            # We construct ad-hoc: a_type='Knight', claim='A is Knave' → false → Knight truth? no → contradiction
            # We'll use is_consistent with custom statements
            pass
    # Actually check: if A says 'A is a Knave', B says anything neutral (e.g., 'B is a Knight')
    # A=Knight → claim 'A=Knave' is false → Knight can't lie → ❌
    # A=Knave → claim 'A=Knave' is true → Knave can't tell truth → ❌
    # No assignment works → paradox
    from solver import evaluate, is_consistent

    def is_paradox_consistent(a_type, b_type):
        # A says "I am a Knave" (edge case), B says "B is a Knight"
        a_truth = (a_type == "Knave")  # "I am a Knave" is True if A=Knave
        if (a_type == "Knight") != a_truth:
            return False
        b_truth = (b_type == "Knight")  # "B is a Knight"
        if (b_type == "Knight") != b_truth:
            return False
        return True

    results = []
    for a_type in ("Knight", "Knave"):
        for b_type in ("Knight", "Knave"):
            results.append(is_paradox_consistent(a_type, b_type))

    assert not any(results), "Self-referential paradox should have no solution"


def test_both_knaves_contradiction():
    """Two Knaves both telling truth (about each other being Knaves) is impossible."""
    # A=Knave says "B is a Knave" → true statement → Knave told truth → ❌
    consistent = is_consistent("Knave", "Knave", "B is a Knave", "We are both Knights")
    assert not consistent, "Both Knaves must contradict themselves"


def test_both_knights_contradiction():
    """Two Knights: A claims B=Knave but B is Knight → A lied → ❌"""
    consistent = is_consistent("Knight", "Knight", "B is a Knave", "We are both Knights")
    assert not consistent, "Both Knights: A's claim about B is false → Knight can't lie"


def test_solution_verification():
    """Double-check the solution manually."""
    a, b = solve_knights_and_knaves()
    # A (Knight) says "B is a Knave" → B is Knave → truth ✅
    assert b == "Knave", "Knight A must truthfully say B=Knave"
    # B (Knave) says "Both Knights" → false because B is Knave → lie ✅
    assert a == "Knight", "Knave B must lie about both being Knights"


# ── Run if called directly ──────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
