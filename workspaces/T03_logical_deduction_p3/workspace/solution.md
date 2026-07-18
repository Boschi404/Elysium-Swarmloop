# Solution: Syllogism Validity

## Evaluation
**Valid?** No.

## Fallacy
**Undistributed Middle Term** — the middle term ("logical people") appears in both premises but never refers to all logical people. Premise 2 says *some* logical people are mathematicians, but we don't know if those "some" overlap with the programmers.

## Counterexample
```
Domain: {Alice, Bob}

P(x) = "x is a programmer"      → True only for Alice
L(x) = "x is logical"           → True for Alice and Bob
M(x) = "x is a mathematician"   → True only for Bob

Check:
  ∀x (P(x) → L(x))   → P(Alice)→L(Alice) ✓, P(Bob)→L(Bob) ✓  → TRUE
  ∃x (L(x) ∧ M(x))   → L(Bob) ∧ M(Bob) ✓                       → TRUE
  ∃x (P(x) ∧ M(x))   → P(Alice) ∧ M(Alice)? No.                → FALSE

Premises TRUE, conclusion FALSE → INVALID
```

## Auto-Test
A quick Python check is included to verify the counterexample.
