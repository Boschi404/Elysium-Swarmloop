#!/usr/bin/env python3
"""Tests for the Knights & Knaves puzzle solver."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solve import statement_a, statement_b, solve


def test_all_cases_enumeration():
    """Exactly one solution should exist."""
    solutions = solve()
    assert len(solutions) == 1, f"Expected 1 solution, got {len(solutions)}"
    a, b, desc = solutions[0]
    assert a == "Knight", f"A should be Knight, got {a}"
    assert b == "Knave", f"B should be Knave, got {b}"


def test_statement_a_knight_truth():
    """If A=Knight, A's statement 'B is Knave' must be true → B=Knave."""
    assert statement_a("Knight", "Knave") == True
    assert statement_a("Knight", "Knight") == False


def test_statement_a_knave_lie():
    """If A=Knave, A's statement 'B is Knave' must be false → B=Knight."""
    assert statement_a("Knave", "Knight") == True
    assert statement_a("Knave", "Knave") == False


def test_statement_b_knight_truth():
    """If B=Knight, B's statement 'both Knights' must be true → A=Knight."""
    assert statement_b("Knight", "Knight") == True
    assert statement_b("Knave", "Knight") == False


def test_statement_b_knave_lie():
    """If B=Knave, B's statement 'both Knights' must be false → at least one Knave."""
    assert statement_b("Knight", "Knave") == True   # not both Knights → lie is true
    assert statement_b("Knave", "Knave") == True    # not both Knights → lie is true


def test_case_1_a_knight_b_knight_inconsistent():
    """Case 1: A=Knight, B=Knight.
       A truth → B must be Knave, but B is Knight → CONTRADICTION."""
    a_ok = statement_a("Knight", "Knight")
    b_ok = statement_b("Knight", "Knight")
    assert not (a_ok and b_ok), "A=Knight,B=Knight should be inconsistent"


def test_case_2_a_knight_b_knave_consistent():
    """Case 2: A=Knight, B=Knave.
       A truth → B is Knave ✓.
       B lie → 'both Knights' is false ✓ (A is Knight, B is Knave).
       → CONSISTENT (this is the solution)."""
    a_ok = statement_a("Knight", "Knave")
    b_ok = statement_b("Knight", "Knave")
    assert a_ok and b_ok, "A=Knight,B=Knave should be consistent"


def test_case_3_a_knave_b_knight_inconsistent():
    """Case 3: A=Knave, B=Knight.
       A lie → B is NOT Knave → B=Knight ✓.
       B truth → both Knights → A must be Knight, but A is Knave → CONTRADICTION."""
    a_ok = statement_a("Knave", "Knight")
    b_ok = statement_b("Knave", "Knight")
    assert not (a_ok and b_ok), "A=Knave,B=Knight should be inconsistent"


def test_case_4_a_knave_b_knave_inconsistent():
    """Case 4: A=Knave, B=Knave.
       A lie → B is NOT Knave → B must be Knight, but B is Knave → CONTRADICTION.
       (Already fails on A's statement alone.)"""
    a_ok = statement_a("Knave", "Knave")
    assert not a_ok, "A=Knave,B=Knave should fail on A's statement"
