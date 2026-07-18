# T01_mathematical_reasoning — Linear Equations System

## System

```
 2x + 3y -  z =  8   (1)
 -x + 4y + 2z =  5   (2)
 3x -  y + 4z = 12   (3)
```

---

## Step 1 — Express z from (1)

```
2x + 3y - z = 8
       -z = 8 - 2x - 3y
        z = 2x + 3y - 8                 (1')
```

---

## Step 2 — Substitute into (2)

```
-x + 4y + 2(2x + 3y - 8) = 5
-x + 4y + 4x + 6y - 16 = 5
3x + 10y - 16 = 5
3x + 10y = 21                           (4)
```

---

## Step 3 — Substitute into (3)

```
3x - y + 4(2x + 3y - 8) = 12
3x - y + 8x + 12y - 32 = 12
11x + 11y - 32 = 12
11x + 11y = 44
  x +   y =  4                           (5)
```

---

## Step 4 — Express y from (5)

```
y = 4 - x                               (5')
```

---

## Step 5 — Substitute into (4)

```
3x + 10(4 - x) = 21
3x + 40 - 10x = 21
-7x + 40 = 21
-7x = -19
 x = 19/7
```

---

## Step 6 — Back-substitute to find y

```
y = 4 - 19/7
y = 28/7 - 19/7
y = 9/7
```

---

## Step 7 — Back-substitute to find z

```
z = 2(19/7) + 3(9/7) - 8
z = 38/7 + 27/7 - 56/7
z = 9/7
```

---

## Solution

```
x = 19/7  ≈ 2.7142857...
y =  9/7  ≈ 1.2857142...
z =  9/7  ≈ 1.2857142...
```

---

## Verification

**Equation (1):**
```
2(19/7) + 3(9/7) - 9/7
= 38/7 + 27/7 - 9/7
= 56/7
= 8  ✅
```

**Equation (2):**
```
-(19/7) + 4(9/7) + 2(9/7)
= -19/7 + 36/7 + 18/7
= 35/7
= 5  ✅
```

**Equation (3):**
```
3(19/7) - 9/7 + 4(9/7)
= 57/7 - 9/7 + 36/7
= 84/7
= 12  ✅
```

All three equations are satisfied.
