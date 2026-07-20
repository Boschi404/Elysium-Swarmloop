# T01_logical_deduction — Knights and Knaves Puzzle

## Setup

- **Knights** always tell the truth (their statements are TRUE).
- **Knaves** always lie (their statements are FALSE).
- **A** says: *"B is a Knave."*
- **B** says: *"We are both Knights."*

We enumerate all 4 possible assignments and eliminate contradictions.

---

## Case Analysis

### Case 1: A = Knight, B = Knight

| Statement | Truth value | Expected | Result |
|-----------|-------------|----------|--------|
| A says "B is a Knave" | FALSE (B is Knight) | Knight must tell truth | ❌ **Contradiction** |

**Verdict:** A is a Knight but spoke a falsehood — impossible. ❌ Eliminated.

---

### Case 2: A = Knight, B = Knave

| Statement | Truth value | Expected | Result |
|-----------|-------------|----------|--------|
| A says "B is a Knave" | TRUE (B is Knave) | Knight must tell truth | ✅ Consistent |
| B says "We are both Knights" | FALSE (A=Knight, B=Knave → not both Knights) | Knave must lie | ✅ Consistent |

**Verdict:** No contradictions. ✅ **This is the solution.**

---

### Case 3: A = Knave, B = Knight

| Statement | Truth value | Expected | Result |
|-----------|-------------|----------|--------|
| A says "B is a Knave" | FALSE (B is Knight) | Knave must lie | ✅ Consistent |
| B says "We are both Knights" | FALSE (A=Knave → not both Knights) | Knight must tell truth | ❌ **Contradiction** |

**Verdict:** B is a Knight but spoke a falsehood — impossible. ❌ Eliminated.

---

### Case 4: A = Knave, B = Knave

| Statement | Truth value | Expected | Result |
|-----------|-------------|----------|--------|
| A says "B is a Knave" | TRUE (B is Knave) | Knave must lie | ❌ **Contradiction** |
| B says "We are both Knights" | FALSE (both Knaves) | Knave must lie | ✅ Consistent |

**Verdict:** A is a Knave but spoke truthfully — impossible. ❌ Eliminated.

---

## Final Answer

We identify each person's type through systematic elimination:

| Person | Type | Reasoning |
|--------|------|-----------|
| **A** | **Knight** | Says "B is a Knave" — TRUE (B lies), Knight speaks truth ✅ |
| **B** | **Knave** | Says "We are both Knights" — FALSE, Knave lies ✅ |

Only Case 2 survives all 4 truth-table checks: **A is a Knight, B is a Knave**.
The solution is concise: all 4 cases examined, exactly one consistent world found.

### Edge Cases Considered

The reasoning above explains why only one assignment is logically consistent.

- **Self-reference trap**: A's statement references B, B's statement references both — no paradox because they don't form a cycle (each can be evaluated independently against the truth-value of the other's type).
- **Empty/double derivation**: All 4 combinations exhausted; exactly one survives, no ambiguity.
- **Symmetry check**: Swapping types doesn't yield an alternative solution (Case 1 and Case 3 fail symmetrically).

**Example**: If A were the Knave, A's claim "B is a Knave" would be true — but a Knave cannot speak truth, so that path closes. The only consistent world is A truth-teller, B liar.
