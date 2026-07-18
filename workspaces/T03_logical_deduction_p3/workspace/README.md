# T03: Logical Deduction — Syllogism Validity Check

## Syllogism
> All programmers are logical.
> Some logical people are mathematicians.
> Therefore, some programmers are mathematicians.

## Verdict: **INVALID** ❌

### Reason
This commits the **Fallacy of the Undistributed Middle Term**.

- Premise 1: P ⊆ L  (Programmers are a subset of Logical people)
- Premise 2: L ∩ M ≠ ∅  (Logical people and Mathematicians intersect)
- Conclusion: P ∩ M ≠ ∅  ❌ — does not follow

The "some logical people" who are mathematicians may be a **different** region of L than the programmers. There is no guarantee of overlap between P and M.

### Counterexample (Set Notation)
```
P = {Alice}              (Programmers)
L = {Alice, Bob}         (Logical people)
M = {Bob}                (Mathematicians)
```
- All programmers are logical: ✅ Alice ∈ L
- Some logical people are mathematicians: ✅ Bob ∈ L ∩ M
- Some programmers are mathematicians: ❌ P ∩ M = ∅

### Venn Diagram
```
 ┌─────────────────────────┐
 │      LOGICAL (L)        │
 │  ┌──────┐  ┌─────────┐ │
 │  │  P   │  │   M     │ │
 │  │Alice │  │  Bob    │ │
 │  └──────┘  └─────────┘ │
 └─────────────────────────┘
```
P is fully inside L. M has a non-empty overlap with L. But P and M are disjoint — the overlap of L and M falls entirely outside P.

### Formal Notation
| Step | Statement | Justification |
|------|-----------|---------------|
| 1 | ∀x (P(x) → L(x)) | Premise 1 |
| 2 | ∃x (L(x) ∧ M(x)) | Premise 2 |
| 3 | ∃x (P(x) ∧ M(x)) | ❌ Invalid conclusion |

There exists an interpretation (the counterexample above) where premises 1 and 2 are true but the conclusion is false. Therefore the argument is **logically invalid**.
