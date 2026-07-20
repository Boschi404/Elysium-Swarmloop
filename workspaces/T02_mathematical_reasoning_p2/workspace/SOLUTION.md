# T02 — Bayes Theorem: Disease Testing

## Problem

A disease affects **1%** of the population. A test is **95% accurate** (both sensitivity and specificity). If someone tests positive, what is the probability they actually have the disease?

---

## Solution (Bayes' Theorem)

### Notation

| Symbol | Meaning | Value |
|--------|---------|-------|
| P(D) | Prior probability of disease | 0.01 |
| P(¬D) | Prior probability of no disease | 0.99 |
| P(T+\|D) | Sensitivity (true positive rate) | 0.95 |
| P(T-\|¬D) | Specificity (true negative rate) | 0.95 |
| P(T+\|¬D) | False positive rate | 0.05 (= 1 − 0.95) |

---

### Step 1 — Total Probability of a Positive Test

The law of total probability gives the denominator for Bayes:

```
P(T+) = P(T+|D) · P(D)  +  P(T+|¬D) · P(¬D)
     = 0.95 × 0.01      +  0.05 × 0.99
     = 0.0095           +  0.0495
     = 0.059
```

So **5.9%** of the population tests positive.

---

### Step 2 — Bayes' Theorem

```
P(D|T+) = P(T+|D) × P(D) / P(T+)
        = 0.95 × 0.01  /  0.059
        = 0.0095       /  0.059
        = 0.1610169...
```

---

### Result

```
P(D|T+) ≈ 0.161  (≈ 16.1%)
```

---

### Intuitive Explanation

Out of **1000 people**:

| Group | Count | Test Positive | Reason |
|-------|-------|---------------|--------|
| Actually sick | 10 | ~10 | 95% of 10 = 9.5 (≈10) true positives |
| Actually healthy | 990 | ~50 | 5% of 990 = 49.5 (≈50) false positives |
| **Total positive** | | **~59** | |

```
P(D|T+)  =  True Positives  /  Total Positives
         ≈  10              /  59
         ≈  0.169
```

The probability is low (~16%) because the disease is rare (1%). Even with a highly accurate test, most positive results are false positives — simply because there are far more healthy people than sick ones.

This is the classic **base rate fallacy**: people intuitively expect a "95% accurate" test to mean a positive result is 95% certain, but Bayes shows it's only ~16%.

---

### Files

- `bayes_solution.py` — Runnable Python script with full step-by-step calculation
- `tests/expected.json` — Expected answer (0.161)
