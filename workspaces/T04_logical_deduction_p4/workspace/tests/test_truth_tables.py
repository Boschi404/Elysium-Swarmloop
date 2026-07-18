#!/usr/bin/env python3
"""Tests for T04_logical_deduction — Truth Table Construction."""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import itertools

# ── Logic helpers ────────────────────────────────────────────────────────

def implies(a, b):
    return (not a) or b

# ── Expressions under test ───────────────────────────────────────────────

def expr_a(p, q, r):
    """(P → Q) ∧ (Q → R) → (P → R)"""
    antecedent = implies(p, q) and implies(q, r)
    consequent = implies(p, r)
    return implies(antecedent, consequent)

def expr_b_lhs(p, q, r):
    """(P → Q) ∧ (¬P → R)"""
    return implies(p, q) and implies(not p, r)

def expr_b_rhs(p, q, r):
    """(P ∧ Q) ∨ (¬P ∧ R)"""
    return (p and q) or ((not p) and r)

# ── Tests ────────────────────────────────────────────────────────────────

def test_part_a_tautology():
    """Every row of (P→Q)∧(Q→R)→(P→R) must be True."""
    for p, q, r in itertools.product([True, False], repeat=3):
        assert expr_a(p, q, r) is True, f"FAIL at P={p}, Q={q}, R={r}"
    print("✅ test_part_a_tautology: PASS (all 8 rows True)")

def test_part_a_rows():
    """Check specific rows of the truth table."""
    # Row: P=T, Q=T, R=F → antecedent=(T→T)∧(T→F)=T∧F=F → (F→F)=T
    assert expr_a(True, True, False) is True
    # Row: P=T, Q=F, R=T → antecedent=(T→F)∧(F→T)=F∧T=F → (F→T)=T
    assert expr_a(True, False, True) is True
    print("✅ test_part_a_rows: PASS (spot-checked key rows)")

def test_part_a_all_antecedent_true():
    """When antecedent is True, consequent must also be True."""
    for p, q, r in itertools.product([True, False], repeat=3):
        antecedent = implies(p, q) and implies(q, r)
        consequent = implies(p, r)
        if antecedent:
            assert consequent is True, f"FAIL: antecedent true but consequent false at {p},{q},{r}"
    print("✅ test_part_a_all_antecedent_true: PASS (hypothetical syllogism)")

def test_part_b_equivalence():
    """(P→Q)∧(¬P→R)  must equal  (P∧Q)∨(¬P∧R) for all 8 rows."""
    for p, q, r in itertools.product([True, False], repeat=3):
        lhs = expr_b_lhs(p, q, r)
        rhs = expr_b_rhs(p, q, r)
        assert lhs == rhs, f"FAIL row P={p}, Q={q}, R={r}: LHS={lhs} ≠ RHS={rhs}"
    print("✅ test_part_b_equivalence: PASS (all 8 rows match)")

def test_part_b_specific_rows():
    """Spot-check specific equivalence rows."""
    # P=T, Q=T, R=T → LHS: (T→T)∧(F→T)=T∧T=T; RHS: (T∧T)∨(F∧T)=T∨F=T
    assert expr_b_lhs(True, True, True) == expr_b_rhs(True, True, True)
    # P=F, Q=T, R=F → LHS: (F→T)∧(T→F)=T∧F=F; RHS: (F∧T)∨(T∧F)=F∨F=F
    assert expr_b_lhs(False, True, False) == expr_b_rhs(False, True, False)
    # P=F, Q=F, R=F → LHS: (F→F)∧(T→F)=T∧F=F; RHS: (F∧F)∨(T∧F)=F∨F=F
    assert expr_b_lhs(False, False, False) == expr_b_rhs(False, False, False)
    print("✅ test_part_b_specific_rows: PASS (spot-checked key rows)")

def test_part_b_degenerate_equivalence():
    """If P is True, both sides reduce to Q."""
    for q, r in itertools.product([True, False], repeat=2):
        assert expr_b_lhs(True, q, r) == q, f"P=T case fail: Q={q}, R={r}"
        assert expr_b_rhs(True, q, r) == q, f"P=T case fail: Q={q}, R={r}"
    print("✅ test_part_b_degenerate_equivalence: PASS (P=T → both reduce to Q)")

def test_part_b_not_p_fallthrough():
    """If P is False, both sides reduce to R."""
    for p, r in itertools.product([True, False], repeat=2):
        if not p:
            assert expr_b_lhs(p, False, r) == r, f"¬P case fail: P={p}, R={r}"
            assert expr_b_rhs(p, False, r) == r, f"¬P case fail: P={p}, R={r}"
    print("✅ test_part_b_not_p_fallthrough: PASS (P=F → both reduce to R)")

# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_part_a_tautology,
        test_part_a_rows,
        test_part_a_all_antecedent_true,
        test_part_b_equivalence,
        test_part_b_specific_rows,
        test_part_b_degenerate_equivalence,
        test_part_b_not_p_fallthrough,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"❌ {t.__name__}: FAIL — {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {t.__name__}: ERROR — {e}")
            failed += 1
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"  Results:  {passed}/{total} passed,  {failed} failed")
    sys.exit(0 if failed == 0 else 1)
