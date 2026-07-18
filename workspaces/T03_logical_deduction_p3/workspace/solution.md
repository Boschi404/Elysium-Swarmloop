# T03: Logical Deduction — Syllogism Validity Check

## Syllogism

> **Premise 1:** All programmers are logical.  
> **Premise 2:** Some logical people are mathematicians.  
> **Conclusion:** Therefore, some programmers are mathematicians.

**Verdict: ❌ INVALID** (Fallacy of the Undistributed Middle / First Figure Fallacy)

---

## Why It Fails

In categorical logic, the minor term (P — programmers) appears in the first premise, the major term (M — mathematicians) in the second, and the middle term (L — logical people) appears in both premises but is **never distributed** (never refers to *all* logical people).

- Premise 1 tells us: **P ⊆ L** — every programmer lives inside the Logical set.
- Premise 2 tells us: **L ∩ M ≠ ∅** — at least one logical person is also a mathematician.
- **Conclusion needs:** **P ∩ M ≠ ∅** — at least one person is both a programmer and a mathematician.

The gap: the logical-mathematician overlap might be **entirely outside** the programmer set. Premises don't forbid it, so the conclusion doesn't follow.

---

## Venn Diagram Proof

```
         ┌─────────────────────┐
         │     LOGICAL (L)     │
         │  ┌──────┐  ┌──────┐ │
         │  │  P   │  │  M   │ │
         │  │ 🧑‍💻  │  │ 🧮  │ │
         │  │      │  │      │ │
         │  └──────┘  └──────┘ │
         │                     │
         └─────────────────────┘
   P = programmers  (subset of L)
   M = mathematicians  (intersects L)
   P ∩ M = ∅  ← counterexample region
```

- **Region A** (P ∩ ¬M): Programmers who are logical but not mathematicians. Filled by {Alice, Bob}.
- **Region B** (M ∩ ¬P ∧ L): Mathematicians who are logical but not programmers. Filled by {Charlie, Dave}.
- **Region C** (P ∩ M): **Empty** in the counterexample — no programmer is a mathematician.

Both premises hold (P ⊆ L ✓, L ∩ M ≠ ∅ ✓), yet **P ∩ M = ∅** — directly disproving the conclusion.

---

## Formal Counterexample (Set Notation)

Let the universe *U* = {Alice, Bob, Charlie, Dave, Ella}

| Set | Members | |
|-----|---------|--|
| P = programmers | {Alice, Bob} | |
| L = logical people | {Alice, Bob, Charlie, Dave} | Ella is illogical |
| M = mathematicians | {Charlie, Dave} | |

**Verification:**

1. **P ⊆ L?** {Alice, Bob} ⊆ {Alice, Bob, Charlie, Dave} → ✅ (all programmers are logical)
2. **L ∩ M ≠ ∅?** {Alice, Bob, Charlie, Dave} ∩ {Charlie, Dave} = {Charlie, Dave} ≠ ∅ → ✅ (some logical people are mathematicians)
3. **P ∩ M ≠ ∅?** {Alice, Bob} ∩ {Charlie, Dave} = ∅ → ❌ (no programmer is a mathematician)

The premises are true, the conclusion is false → **the argument is invalid.**

---

## Why People Get Tricked

This is a well-known **distribution fallacy** (also called the **first-figure fallacy** or **fallacy of the undistributed middle**). The brain intuitively reads *"all programmers are logical"* as *"all logical people are programmers"* (the converse error), which would validate the conclusion — but that's not what the premise says. In formal logic:

- **Universal Affirmative** (A): "All P are L" — distributes the subject P, not the predicate L.
- **Particular Affirmative** (I): "Some L are M" — distributes neither term.
- The middle term L is never distributed → conclusion doesn't follow.

This violates **Rule 2** of the classical syllogism rules: *The middle term must be distributed at least once.*
