# Knights and Knaves — Solution Report

## Problem
On an island, Knights always tell the truth and Knaves always lie.
- **A says:** "B is a Knave."
- **B says:** "We are both Knights."

Determine the identity of A and B.

---

## Truth-Table Analysis (All 4 Cases)

Let `Knight(T)` = always truthful, `Knave(F)` = always lying.

### Case 1 — A = Knight, B = Knight
| Statement | Truth value | Expectation | Result |
|-----------|------------|-------------|--------|
| A: "B is a Knave" | False (B is Knight) | Knight must tell truth | **Contradiction** |
| B: "Both Knights" | True (both are Knights) | Knight must tell truth | Consistent |
| **Verdict** | | | **❌ Impossible** |

### Case 2 — A = Knight, B = Knave  ✅
| Statement | Truth value | Expectation | Result |
|-----------|------------|-------------|--------|
| A: "B is a Knave" | True (B is Knave) | Knight tells truth | Consistent ✅ |
| B: "Both Knights" | False (A≠Knight or B≠Knight) | Knave must lie | Consistent ✅ |
| **Verdict** | | | **✅ SOLUTION** |

### Case 3 — A = Knave, B = Knight
| Statement | Truth value | Expectation | Result |
|-----------|------------|-------------|--------|
| A: "B is a Knave" | False (B is Knight) | Knave must lie | Consistent |
| B: "Both Knights" | False (A is Knave) | Knight must tell truth | **Contradiction** |
| **Verdict** | | | **❌ Impossible** |

### Case 4 — A = Knave, B = Knave
| Statement | Truth value | Expectation | Result |
|-----------|------------|-------------|--------|
| A: "B is a Knave" | True (B is Knave) | Knave must lie | **Contradiction** |
| B: "Both Knights" | True (both Knaves) | Knave must lie | Consistent |
| **Verdict** | | | **❌ Impossible** |

---

## Conclusion

Only **Case 2** is logically consistent:

> **A is a Knight** (always tells truth)  
> **B is a Knave** (always lies)

### Verification
- A (Knight) truthfully says "B is a Knave" → correct, B is a Knave ✓
- B (Knave) falsely says "We are both Knights" → false, since B is not a Knight ✓

### Edge Cases Considered
- **Self-referential paradox**: If A said "I am a Knave", that would be paradoxical (Knight claiming to be Knave is false, Knave claiming to be Knave is true → no consistent assignment). Our puzzle avoids this.
- **Mutual dependency**: Each statement references the other person, which is why the truth-table approach is necessary.
- **Empty/trivial universe**: The puzzle assumes exactly two inhabitants A and B, no third party.

### Example Extension
If a third person C said "A is a Knave", with our solution (A = Knight, B = Knave), C's statement would be False → if C were a Knight, contradiction → so C must be a Knave.
