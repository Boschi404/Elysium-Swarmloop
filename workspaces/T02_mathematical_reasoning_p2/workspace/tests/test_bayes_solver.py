"""
Tests for the Bayes Theorem solver.

Verifies:
1. The classic disease-test problem returns ~16.1%
2. Perfect test with perfect prevalence returns 100%
3. Zero prevalence returns 0%
4. Symmetry: 50% prevalence with equal sensitivity/specificity
5. Multiple variants
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bayes_solver import bayes_disease_test


def test_classic_problem():
    """Standard 1% prevalence, 95% sens/spec → ~16.1%"""
    result = bayes_disease_test(prevalence=0.01, sensitivity=0.95, specificity=0.95, verbose=False)
    expected = 0.161017
    assert abs(result["p_disease_given_positive"] - expected) < 0.001, (
        f"Expected ~{expected:.4f}, got {result['p_disease_given_positive']:.6f}"
    )
    print(f"  PASS: classic problem → {result['p_disease_given_positive']:.4f} (expected ~{expected:.4f})")


def test_perfect_test():
    """Perfect sensitivity and specificity → always 100%"""
    for prev in [0.01, 0.5, 0.99]:
        result = bayes_disease_test(prevalence=prev, sensitivity=1.0, specificity=1.0, verbose=False)
        assert abs(result["p_disease_given_positive"] - 1.0) < 1e-9, (
            f"Perfect test with prevalence={prev} should be 1.0, got {result['p_disease_given_positive']}"
        )
    print("  PASS: perfect test → 1.0 for all prevalence values")


def test_zero_prevalence():
    """If no one has the disease, P(D|T+) = 0"""
    result = bayes_disease_test(prevalence=0.0, sensitivity=0.95, specificity=0.95, verbose=False)
    assert result["p_disease_given_positive"] == 0.0, (
        f"Zero prevalence should give 0, got {result['p_disease_given_positive']}"
    )
    print("  PASS: zero prevalence → 0.0")


def test_fifty_percent_prevalence():
    """With 50% prevalence and symmetric 95% test, result should be exactly 0.95"""
    result = bayes_disease_test(prevalence=0.5, sensitivity=0.95, specificity=0.95, verbose=False)
    expected = 0.95  # (0.95 * 0.5) / (0.95*0.5 + 0.05*0.5) = 0.95
    assert abs(result["p_disease_given_positive"] - expected) < 1e-9, (
        f"50% prev + 95% test should be {expected}, got {result['p_disease_given_positive']}"
    )
    print(f"  PASS: symmetrical 50% prevalence → {result['p_disease_given_positive']}")


def test_bayes_formula_structure():
    """Verify the return dict has all expected keys and correct structure"""
    result = bayes_disease_test(verbose=False)
    expected_keys = {
        "p_disease_given_positive",
        "p_positive",
        "p_false_positive",
        "true_positive_rate",
        "false_positive_rate",
        "n_true_positives_per_10k",
        "n_false_positives_per_10k",
    }
    assert set(result.keys()) == expected_keys, (
        f"Keys mismatch: expected {expected_keys}, got {set(result.keys())}"
    )
    print(f"  PASS: all {len(expected_keys)} expected keys present")


def test_manually_computed():
    """Manual computation: P(D|T+) for 1% prev, 90% sens, 90% spec"""
    # P(T+) = 0.9*0.01 + 0.1*0.99 = 0.009 + 0.099 = 0.108
    # P(D|T+) = 0.009 / 0.108 = 0.08333...
    result = bayes_disease_test(prevalence=0.01, sensitivity=0.9, specificity=0.9, verbose=False)
    expected = 0.009 / 0.108
    assert abs(result["p_disease_given_positive"] - expected) < 1e-6, (
            f"Expected {expected:.10f}, got {result['p_disease_given_positive']:.10f}"
        )
    print(f"  PASS: manual computation → {result['p_disease_given_positive']:.6f}")


def test_low_prevalence_edge():
    """Very rare disease (0.01%) with 99% sens/spec"""
    p = 0.0001
    sens = 0.99
    spec = 0.99
    result = bayes_disease_test(prevalence=p, sensitivity=sens, specificity=spec, verbose=False)
    # Manual: P(T+) = 0.99*0.0001 + 0.01*0.9999 = 0.000099 + 0.009999 = 0.010098
    # P(D|T+) = 0.000099 / 0.010098 ≈ 0.0098
    expected = (sens * p) / (sens * p + (1 - spec) * (1 - p))
    assert abs(result["p_disease_given_positive"] - expected) < 1e-6, (
        f"Expected {expected:.8f}, got {result['p_disease_given_positive']:.8f}"
    )
    print(f"  PASS: rare disease → {result['p_disease_given_positive']:.6f}")


def test_round_trip():
    """Using bayes solver in other calculations"""
    result = bayes_disease_test(prevalence=0.01, sensitivity=0.95, specificity=0.95, verbose=False)
    # Total probability should sum correctly
    assert abs(result["p_positive"] - 0.059) < 0.001, (
        f"P(T+) should be 0.059, got {result['p_positive']}"
    )
    print(f"  PASS: P(T+) = {result['p_positive']:.4f} (expected 0.059)")


if __name__ == "__main__":
    print("\nBayes Solver — Test Suite\n" + "=" * 40)
    tests = [
        test_classic_problem,
        test_perfect_test,
        test_zero_prevalence,
        test_fifty_percent_prevalence,
        test_bayes_formula_structure,
        test_manually_computed,
        test_low_prevalence_edge,
        test_round_trip,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {test.__name__}: {e}")
            failed += 1
    print(f"\n{'=' * 40}")
    print(f"Result: {passed} passed, {failed} failed out of {len(tests)} tests")
    sys.exit(0 if failed == 0 else 1)
