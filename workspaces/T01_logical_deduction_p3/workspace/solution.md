# T01 Logical Deduction — Knights and Knaves Puzzle

## Problem
On an island, Knights always tell the truth, Knaves always lie.
This puzzle tests the ability to **identify** contradictions in logical statements.

- **A says:** "B is a Knave."
- **B says:** "We are both Knights."

Determine who is a Knight and who is a Knave.

---

## Solution

### Case analysis of all 4 possibilities

| Case | A | B | A's statement true? | B's statement true? | Consistent? |
|------|---|---|---------------------|---------------------|-------------|
| 1    | Knight | Knight | "B is Knave" — **false** (Knight can't lie) | — | ❌ |
| 2    | **Knight** | **Knave** | "B is Knave" — **true** ✅ | "Both Knights" — **false** (Knave must lie) ✅ | ✅ |
| 3    | Knave | Knight | "B is Knave" — **false** (Knave must lie) ✅ | "Both Knights" — **false** (Knight can't lie) | ❌ |
| 4    | Knave | Knave | "B is Knave" — **true** (Knave must lie) | — | ❌ |

### Contradictions eliminated

**Case 1** (A=Knight, B=Knight):  
A tells truth, so "B is a Knave" would be true → B would be Knave. But B is Knight. Contradiction. ✗

**Case 2** (A=Knight, B=Knave):  
- A (Knight, truth-teller) says "B is a Knave" — B is indeed a Knave. ✓  
- B (Knave, liar) says "We are both Knights" — they are not both Knights. False statement from a liar. ✓  
→ **No contradiction. This is the only valid solution.** ✓

**Case 3** (A=Knave, B=Knight):  
- A (Knave, liar) says "B is a Knave" — B is Knight, so this is a false statement. Liar lying. ✓  
- B (Knight, truth-teller) says "We are both Knights" — but A is Knave, so this would be false. A Knight cannot lie. ✗

**Case 4** (A=Knave, B=Knave):  
- A (Knave, liar) says "B is a Knave" — B IS a Knave, so this is a TRUE statement. A liar cannot tell truth. ✗

### Final answer

> **A is a Knight, B is a Knave.**

These results **explain** the only consistent assignment: A's truthful claim matches B's Knave nature, and B's false claim matches his liar role.

---

## Edge cases & observations

- **Self-referential traps:** Neither statement is purely self-referential (A talks about B, B talks about both), avoiding infinite loops.
- **Mutual exclusivity:** The two roles (Knight/Knave) are exhaustive and mutually exclusive — every islander is exactly one or the other.
- **Verification:** A says truth (B is Knave ✓), B lies (both Knights — false ✓). No inconsistencies.
- **Example extension:** If a third person C entered and said "A is a Knave," we could chain deductions further.

---

## Concise summary

Only 1 of 4 type assignments is contradiction-free:
- **A = Knight, B = Knave** — all statements match their roles.
