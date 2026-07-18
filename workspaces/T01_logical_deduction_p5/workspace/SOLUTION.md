# Knights and Knaves Puzzle — Solution

## The Puzzle
On a mysterious island:
- **Knights** always tell the truth.
- **Knaves** always lie.

> **A says:** "B is a Knave."
> **B says:** "We are both Knights."

Determine who is a Knight and who is a Knave.

---

## Case Analysis

### Case 1: A = Knight, B = Knight
| Person | Statement | Expected | Actual | Result |
|--------|-----------|----------|--------|--------|
| A (Knight) | "B is a Knave" | Must be TRUE | B is Knight → FALSE | ❌ Contradiction |
| B (Knight) | "We are both Knights" | Must be TRUE | Both Knights → TRUE | ✅ |

**Verdict:** A lied while being a Knight → **IMPOSSIBLE** ✗

---

### Case 2: A = Knight, B = Knave ✅
| Person | Statement | Expected | Actual | Result |
|--------|-----------|----------|--------|--------|
| A (Knight) | "B is a Knave" | Must be TRUE | B is Knave → TRUE | ✅ |
| B (Knave) | "We are both Knights" | Must be FALSE | Not both Knights → FALSE | ✅ |

**Verdict:** Both consistent → **SOLUTION FOUND** ✓

---

### Case 3: A = Knave, B = Knight
| Person | Statement | Expected | Actual | Result |
|--------|-----------|----------|--------|--------|
| A (Knave) | "B is a Knave" | Must be FALSE | B is Knight → FALSE | ✅ |
| B (Knight) | "We are both Knights" | Must be TRUE | Not both Knights → FALSE | ❌ Contradiction |

**Verdict:** B lied while being a Knight → **IMPOSSIBLE** ✗

---

### Case 4: A = Knave, B = Knave
| Person | Statement | Expected | Actual | Result |
|--------|-----------|----------|--------|--------|
| A (Knave) | "B is a Knave" | Must be FALSE | B is Knave → TRUE | ❌ Contradiction |
| B (Knave) | "We are both Knights" | Must be FALSE | Not both Knights → FALSE | ✅ |

**Verdict:** A told truth while being a Knave → **IMPOSSIBLE** ✗

---

## Conclusion

> **A is a Knight, B is a Knave.**

Only Case 2 satisfies all constraints:
- A (Knight) truthfully states that B is a Knave. ✓
- B (Knave) falsely claims that both are Knights. ✓
