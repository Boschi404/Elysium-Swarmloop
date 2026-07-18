#!/usr/bin/env python3
"""
Tests for T02_logical_deduction — Zebra Puzzle (Einstein's Riddle).

Validates:
  1. The solver produces a correct solution (all 15 clues satisfied)
  2. The solution document meets rubric criteria
  3. All clue verifications pass
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ──────────────────────────────────────────────────────────────
# Helper: import solver without running main()
# ──────────────────────────────────────────────────────────────
SOLVER_PATH = os.path.join(os.path.dirname(__file__), "..", "solve_zebra.py")


def load_solver():
    """Import solve_zebra as a module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("solve_zebra", SOLVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ──────────────────────────────────────────────────────────────
# Test: solver produces valid result
# ──────────────────────────────────────────────────────────────
def test_solver_finds_solution():
    mod = load_solver()
    houses = mod.solve()
    assert houses is not None, "Solver returned None — no solution found"
    assert len(houses) == 5, f"Expected 5 houses, got {len(houses)}"
    for h in houses:
        assert all(k in h for k in ("position", "color", "nationality", "drink", "smoke", "pet"))


def test_all_clues_satisfied():
    mod = load_solver()
    houses = mod.solve()
    checks = mod.verify_all(houses)
    failures = [desc for desc, ok in checks if not ok]
    assert not failures, f"Clue failures: {failures}"
    assert len(checks) >= 17, f"Expected 17+ checks, got {len(checks)}"


def test_zebra_owner():
    mod = load_solver()
    houses = mod.solve()
    zebra_house = next(h for h in houses if h["pet"] == "Zebra")
    assert zebra_house["nationality"] == "German", \
        f"Expected German to own zebra, got {zebra_house['nationality']}"
    assert zebra_house["color"] == "Green", \
        f"Expected green house, got {zebra_house['color']}"
    assert zebra_house["position"] == 4, \
        f"Expected position 4, got {zebra_house['position']}"


def test_uniqueness():
    mod = load_solver()
    houses = mod.solve()
    for attr in ("color", "nationality", "drink", "smoke", "pet"):
        values = [h[attr] for h in houses]
        assert len(set(values)) == 5, f"Duplicate {attr}: {values}"


# ──────────────────────────────────────────────────────────────
# Test: solution.md meets rubric criteria
# ──────────────────────────────────────────────────────────────
SOLUTION_MD = os.path.join(os.path.dirname(__file__), "..", "solution.md")


def _read_solution_md():
    with open(SOLUTION_MD, "r", encoding="utf-8") as f:
        return f.read()


def test_solution_md_exists():
    assert os.path.isfile(SOLUTION_MD), f"Missing: {SOLUTION_MD}"


def test_rubric_correctness():
    """Rubric: contains 'solution', min_length 100, regex zebra|puzzle|einstein"""
    text = _read_solution_md()
    assert "solution" in text.lower(), "Missing 'solution'"
    assert len(text) >= 100, f"Too short: {len(text)} chars"
    assert re.search(r"zebra|puzzle|einstein", text, re.IGNORECASE), \
        "Missing required regex match"


def test_rubric_completeness():
    """Rubric: contains 'identify', 'explain', min_length 200"""
    text = _read_solution_md()
    assert "identify" in text.lower(), "Missing 'identify'"
    assert "explain" in text.lower(), "Missing 'explain'"
    assert len(text) >= 200, f"Too short: {len(text)} chars"


def test_rubric_efficiency():
    """Rubric: contains 'concise', min_length 50"""
    text = _read_solution_md()
    assert "concise" in text.lower(), "Missing 'concise'"
    assert len(text) >= 50, f"Too short: {len(text)} chars"


def test_rubric_robustness():
    """Rubric: contains 'edge case', 'example'"""
    text = _read_solution_md()
    assert "edge case" in text.lower(), "Missing 'edge case'"
    assert "example" in text.lower(), "Missing 'example'"


def test_rubric_clarity():
    """Rubric: has '#' structure, min_length 150"""
    text = _read_solution_md()
    assert "# " in text, "Missing markdown heading structure (#)"
    assert text.count("# ") >= 2, "Need at least 2 headings"
    assert len(text) >= 150, f"Too short: {len(text)} chars"


# ──────────────────────────────────────────────────────────────
# Run all if executed directly
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
