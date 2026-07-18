import sys
import json
import os

# Add workspace to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solution import solve, PersonType


def test_solution_not_none():
    """There must be exactly one consistent solution."""
    result = solve()
    assert result["solution"] is not None, "Expected exactly one solution"


def test_solution_values():
    """A must be Knight, B must be Knave."""
    result = solve()
    assert result["solution"]["A"] == "Knight", f"Expected A=Knight, got A={result['solution']['A']}"
    assert result["solution"]["B"] == "Knave", f"Expected B=Knave, got B={result['solution']['B']}"


def test_only_one_consistent_case():
    """Only case 2 (A=Knight, B=Knave) should be consistent."""
    result = solve()
    consistent_cases = [c for c in result["cases"] if c["consistent"]]
    assert len(consistent_cases) == 1, f"Expected 1 consistent case, got {len(consistent_cases)}"
    assert consistent_cases[0]["A"] == "Knight"
    assert consistent_cases[0]["B"] == "Knave"


def test_all_four_cases_present():
    """All 4 combinations must be enumerated."""
    result = solve()
    assert len(result["cases"]) == 4, f"Expected 4 cases, got {len(result['cases'])}"


def test_knight_truth():
    """If A is Knight, statement 'B is a Knave' must be true."""
    result = solve()
    case2 = result["cases"][1]  # A=Knight, B=Knave
    assert case2["A_consistent"] is True


def test_knave_lie():
    """If B is Knave, statement 'We are both Knights' must be false."""
    result = solve()
    case2 = result["cases"][1]
    assert case2["B_consistent"] is True
    assert case2["B_statement_is_true"] is False


def test_from_json_solution():
    """Verify solution.json matches solution.py."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "solution.json")
    with open(json_path) as f:
        data = json.load(f)
    result = solve()
    py_sol = result["solution"]
    json_sol = data["solution"]
    assert py_sol["A"] == json_sol["A"], f"Mismatch A: py={py_sol['A']} json={json_sol['A']}"
    assert py_sol["B"] == json_sol["B"], f"Mismatch B: py={py_sol['B']} json={json_sol['B']}"
