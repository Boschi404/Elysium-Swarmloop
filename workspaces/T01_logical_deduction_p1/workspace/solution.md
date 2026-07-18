# T01_logical_deduction — Knights & Knaves Puzzle

## The Puzzle

On an island where **Knights always tell the truth** and **Knaves always lie**:

- **A** says: *"B is a Knave."*
- **B** says: *"We are both Knights."*

Determine who is a Knight and who is a Knave.

---

## Solution: A = Knight, B = Knave

### Truth table of all 4 cases

| Case | A | B | A says "B is Knave" | B says "both Knights" | Result |
|------|---|---|----------------------|------------------------|--------|
| 1 | Knight | Knight | B is Knave → **false** ❌ (A would be lying) | both Knights → **true** ✓ | ❌ INCONSISTENT |
| 2 | **Knight** | **Knave** | B is Knave → **true** ✓ | both Knights → **false** ✓ (correct lie by B) | ✅ **SOLUTION** |
| 3 | Knave | Knight | B is Knave → **false** ✓ (correct lie by A) | both Knights → **true** ✓ but A=Knave makes this false | ❌ INCONSISTENT |
| 4 | Knave | Knave | B is Knave → **true** — but A is Knave so it should be **false** | — | ❌ INCONSISTENT |

### Step-by-step reasoning

1. **Case 1 — A=Knight, B=Knight**: A (truthful) says "B is Knave" → B would have to be Knave, but B is Knight → **contradiction**.

2. **Case 2 — A=Knight, B=Knave**: A (truthful) says "B is Knave" → B is Knave, which is true ✓. B (liar) says "both Knights" → this is false (A=Knight, B=Knave) ✓. **All consistent.**

3. **Case 3 — A=Knave, B=Knight**: A (liar) says "B is Knave" → this is false → B is Knight ✓. B (truthful) says "both Knights" → both must be Knights, but A is Knave → **contradiction**.

4. **Case 4 — A=Knave, B=Knave**: A (liar) says "B is Knave" → this should be false → B must be Knight, but B is Knave → **contradiction** (fails immediately).

### Conclusion

> **A is a Knight, B is a Knave.** ✅

---

## Verifying

```
A is Knight → "B is a Knave" is TRUE  → B is Knave ✓
B is Knave  → "We are both Knights" is FALSE → (not both Knights) ✓
```
