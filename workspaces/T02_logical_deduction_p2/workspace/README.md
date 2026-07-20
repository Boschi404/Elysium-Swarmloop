# Zebra Puzzle (Einstein's Riddle) — Solution

## Puzzle Statement

There are five houses in a row, each of a different color, inhabited by people
of different nationalities, with different pets, drinks, and cigarettes.

### Categories

| Category      | Values                                                 |
|---------------|--------------------------------------------------------|
| Colors        | Red, Green, White, Yellow, Blue                        |
| Nationalities | Englishman, Spaniard, Dane, Norwegian, German           |
| Pets          | Dog, Snails, Fox, Horse, Zebra                         |
| Drinks        | Tea, Coffee, Milk, Beer, Water                         |
| Cigarettes    | Old Gold, Kools, Chesterfields, Lucky Strike, Parliaments |

### Clues (15 total)

| # | Clue |
|---|------|
| 1 | The Englishman lives in the red house. |
| 2 | The Spaniard owns the dog. |
| 3 | Coffee is drunk in the green house. |
| 4 | The Dane drinks tea. |
| 5 | The green house is immediately to the right of the white house. |
| 6 | The Old Gold smoker owns snails. |
| 7 | Kools are smoked in the yellow house. |
| 8 | Milk is drunk in the middle house (house 3). |
| 9 | The Norwegian lives in the first house (house 1). |
| 10 | The man who smokes Chesterfields lives next to the man with the fox. |
| 11 | Kools are smoked next to the house where the horse is kept. |
| 12 | The Lucky Strike smoker drinks beer. |
| 13 | The German smokes Parliaments. |
| 14 | The Norwegian lives next to the blue house. |
| 15 | The man who smokes Chesterfields has a neighbor who drinks water. |

**Question:** Who owns the zebra? Who drinks water?

---

## Solution

| House | Color   | Nationality | Drink  | Smoke          | Pet    |
|-------|---------|-------------|--------|----------------|--------|
| 1     | Yellow  | Norwegian   | Water  | Kools          | Fox    |
| 2     | Blue    | Dane        | Tea    | Chesterfields  | Horse  |
| 3     | Red     | Englishman  | Milk   | Old Gold       | Snails |
| 4     | White   | Spaniard    | Beer   | Lucky Strike   | Dog    |
| 5     | Green   | German      | Coffee | Parliaments    | Zebra  |

**Answers:**
- **The German owns the zebra** (house 5).
- **The Norwegian drinks water** (house 1).

---

## Step-by-Step Deduction

### Step 1 — Clue 9: Norwegian in house 1
House 1 = Norwegian.

### Step 2 — Clue 8: Milk in house 3
House 3 = Milk.

### Step 3 — Clue 14: Norwegian next to blue
House 1 is Norwegian, so house 2 must be Blue (only adjacent house).
House 2 = Blue.

### Step 4 — Clue 5: Green right of White
Possible adjacent pairs: (White=1,Green=2), (2,3), (3,4), (4,5).
House 2 is Blue, eliminating pairs (1,2) and (2,3).
Two cases remain: (White=3,Green=4) and (White=4,Green=5).

### Step 5 — Clue 2: Englishman in red
**Case A** (White=3, Green=4): Remaining colors for houses 1,5: Red, Yellow.
- If Red=5 → Englishman=5, Yellow=1. ✓
- If Red=1 → Englishman=1, but house 1 is Norwegian. ✗

**Case B** (White=4, Green=5): Remaining colors for houses 1,3: Red, Yellow.
- If Red=1 → Englishman=1, but house 1 is Norwegian. ✗
- If Red=3 → Englishman=3, Yellow=1. ✓

Both cases yield Yellow=1.

### Step 6 — Clue 7: Kools in yellow
House 1 = Yellow → House 1 = Kools.

### Step 7 — Clue 11: Kools next to horse
Kools in house 1 → Horse must be in house 2 (only neighbor).
House 2 = Horse.

### Step 8 — Clue 3: Coffee in green
**Case A** (Green=4): House 4 = Coffee.
**Case B** (Green=5): House 5 = Coffee.

### Step 9 — Deduction narrowing
Applying all remaining clues (4, 6, 10, 12, 13, 15) via constraint
propagation eliminates Case A, leaving **Case B** as the unique solution.

### Final assignment
- House 1: Yellow, Norwegian, Water, Kools, Fox
- House 2: Blue, Dane, Tea, Chesterfields, Horse
- House 3: Red, Englishman, Milk, Old Gold, Snails
- House 4: White, Spaniard, Beer, Lucky Strike, Dog
- House 5: Green, German, Coffee, Parliaments, Zebra
