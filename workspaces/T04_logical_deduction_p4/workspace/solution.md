# T04 — Logical Deduction: Truth Table Construction

## Solution Overview

This solution builds truth tables for two logical formulae and provides a rigorous analysis of tautology and equivalence properties. All 16 rows (8 per formula) are computed exhaustively using Python.

---

## Part 1: Tautology Proof — `((P → Q) ∧ (Q → R)) → (P → R)`

### Truth Table

| P | Q | R | P→Q | Q→R | (P→Q)∧(Q→R) | P→R | ((P→Q)∧(Q→R))→(P→R) |
|---|---|---|-----|-----|-------------|-----|---------------------|
| 1 | 1 | 1 | 1   | 1   | 1           | 1   | 1                   |
| 1 | 1 | 0 | 1   | 0   | 0           | 0   | 1                   |
| 1 | 0 | 1 | 0   | 1   | 0           | 1   | 1                   |
| 1 | 0 | 0 | 0   | 1   | 0           | 0   | 1                   |
| 0 | 1 | 1 | 1   | 1   | 1           | 1   | 1                   |
| 0 | 1 | 0 | 1   | 0   | 0           | 1   | 1                   |
| 0 | 0 | 1 | 1   | 1   | 1           | 1   | 1                   |
| 0 | 0 | 0 | 1   | 1   | 1           | 1   | 1                   |

### Result: **TAUTOLOGY** ✅

The final column is **all 1s (True)** across every possible assignment of P, Q, R. This proves the principle of **hypothetical syllogism** (transitivity of implication). In formal logic notation:

> If `(P → Q)` and `(Q → R)` are both true, then `(P → R)` must also be true.

### Explanation

- When the antecedent `(P→Q) ∧ (Q→R)` is **False** (rows 2, 3, 4, 6), the implication is **vacuously true**.
- When the antecedent is **True** (rows 1, 5, 7, 8), the consequent `(P→R)` is also True — the chain holds.
- No counterexample exists, confirming tautology.

---

## Part 2: Equivalence Check — `(P → Q) ∧ (¬P → R)` vs `(P ∧ Q) ∨ (¬P ∧ R)`

### Truth Table

| P | Q | R | ¬P | P→Q | ¬P→R | LHS: (P→Q)∧(¬P→R) | P∧Q | ¬P∧R | RHS: (P∧Q)∨(¬P∧R) | LHS↔RHS |
|---|---|---|----|-----|------|-------------------|-----|------|-------------------|---------|
| 1 | 1 | 1 | 0  | 1   | 1    | 1                 | 1   | 0    | 1                 | 1       |
| 1 | 1 | 0 | 0  | 1   | 1    | 1                 | 1   | 0    | 1                 | 1       |
| 1 | 0 | 1 | 0  | 0   | 1    | 0                 | 0   | 0    | 0                 | 1       |
| 1 | 0 | 0 | 0  | 0   | 1    | 0                 | 0   | 0    | 0                 | 1       |
| 0 | 1 | 1 | 1  | 1   | 1    | 1                 | 0   | 1    | 1                 | 1       |
| 0 | 1 | 0 | 1  | 1   | 0    | 0                 | 0   | 0    | 0                 | 1       |
| 0 | 0 | 1 | 1  | 1   | 1    | 1                 | 0   | 1    | 1                 | 1       |
| 0 | 0 | 0 | 1  | 1   | 0    | 0                 | 0   | 0    | 0                 | 1       |

### Result: **LOGICALLY EQUIVALENT** ✅

The `LHS ↔ RHS` column is **True for all 8 rows**, confirming the two expressions always produce identical truth values.

### Edge Cases Identified

1. **P = True, Q = False, R = False**: Both sides evaluate to False. LHS = (T→F)∧(F→F) = F∧T = **F**, RHS = (T∧F)∨(F∧F) = F∨F = **F**.
2. **P = False, Q = True, R = False**: LHS = (F→T)∧(T→F) = T∧F = **F**, RHS = (F∧T)∨(T∧F) = F∨F = **F**.
3. **P = True, Q = True, R = True**: Both evaluate to True — the straightforward case.
4. **P = False, Q = False, R = True**: Both evaluate to True — the implication is vacuously true on the left side.

### Concise Algebraic Justification

Using boolean algebra:
- LHS = (¬P ∨ Q) ∧ (P ∨ R) &nbsp;— rewriting implications
- RHS = (P ∧ Q) ∨ (¬P ∧ R) &nbsp;— DNF form

These are equivalent via the **consensus theorem** and **distributive property**. The truth table confirms the algebraic identity.

---

## Real-World Example

In **digital circuit design**, an engineer tasked with implementing the condition "if sensor A is active then enable motor B, and if sensor A is inactive then activate alarm C" can express this as `(A→B)∧(¬A→C)`. Recognizing that this is equivalent to the simpler DNF `(A∧B)∨(¬A∧C)` allows replacing a multi-gate circuit with a single 2-input AND-OR combination, reducing component count and power consumption.

---

## How to Run

```bash
python "C:\Users\Admin\Elysium-Swarmloop\workspaces\T04_logical_deduction_p4\workspace/truth_table.py"
```

The script prints both formatted truth tables, identifies the tautology, and declares the equivalence result.

## Summary

| Property | Result |
|----------|--------|
| `((P→Q)∧(Q→R)) → (P→R)` is a tautology? | **YES** — hypothetical syllogism proven |
| `(P→Q)∧(¬P→R)` ≟ `(P∧Q)∨(¬P∧R)` | **YES** — logically equivalent |
| Total truth table rows | **16** (8 + 8) |
