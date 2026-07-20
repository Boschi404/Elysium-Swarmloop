# T01: Linear Equations System — Solution

**System:**
```
2x + 3y - z = 8    (1)
-x + 4y + 2z = 5   (2)
3x - y + 4z = 12   (3)
```

## Method: Gaussian Elimination (Row Echelon Form)

### Step 1 — Form the augmented matrix
```
[ 2   3  -1 |  8]
[-1   4   2 |  5]
[ 3  -1   4 | 12]
```

### Step 2 — Forward elimination

**Pivot on R1** — divide by 2 to get leading 1:
```
[ 1   1.5  -0.5 | 4 ]
[-1   4     2   | 5 ]
[ 3  -1     4   | 12]
```

**Eliminate x from R2** (R2 ← R2 + R1):
```
[ 1   1.5  -0.5 | 4 ]
[ 0   5.5   1.5 | 9 ]
[ 3  -1     4   | 12]
```

**Eliminate x from R3** (R3 ← R3 − 3×R1):
```
[ 1   1.5  -0.5 | 4 ]
[ 0   5.5   1.5 | 9 ]
[ 0  -5.5   5.5 | 0 ]
```

**Eliminate y from R3** (R3 ← R3 + R2):
```
[ 1   1.5  -0.5 | 4 ]
[ 0   5.5   1.5 | 9 ]
[ 0   0     7   | 9 ]
```

### Step 3 — Back substitution

**From R3 (row 3):** `7z = 9` → **z = 9/7 ≈ 1.285714**

**From R2 (row 2):** `5.5y + 1.5z = 9`
```
5.5y + 1.5(9/7) = 9
5.5y + 13.5/7 = 9
5.5y = 63/7 - 13.5/7 = 49.5/7
y = 49.5/38.5 = 99/77 = 9/7
```
→ **y = 9/7 ≈ 1.285714**

**From R1 (row 1):** `x + 1.5y - 0.5z = 4`
```
x + 1.5(9/7) - 0.5(9/7) = 4
x + (13.5/7 - 4.5/7) = 4
x + 9/7 = 4
x = 28/7 - 9/7 = 19/7
```
→ **x = 19/7 ≈ 2.714286**

## Final Solution
```
x = 19/7 ≈ 2.7142857143
y = 9/7  ≈ 1.2857142857
z = 9/7  ≈ 1.2857142857
```

## Verification

Substitute back into the original equations:

**Equation (1):** `2(19/7) + 3(9/7) - (9/7) = 38/7 + 27/7 - 9/7 = 56/7 = 8 ✓`

**Equation (2):** `-(19/7) + 4(9/7) + 2(9/7) = -19/7 + 36/7 + 18/7 = 35/7 = 5 ✓`

**Equation (3):** `3(19/7) - (9/7) + 4(9/7) = 57/7 - 9/7 + 36/7 = 84/7 = 12 ✓`

All three equations hold. The solution is correct.
