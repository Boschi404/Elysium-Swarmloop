# Bayes Theorem — Disease Testing Problem

**Problem**: A disease affects 1% of the population. A test has 95% sensitivity and 95% specificity.
If someone tests positive, what is the probability they actually have the disease?

---

## Step 1: Define Events

- **D** = Person has the disease
- **T⁺** = Test is positive

## Step 2: Given Probabilities

| Symbol | Value | Meaning |
|--------|-------|---------|
| P(D) | 0.01 (1%) | Prevalence — disease in population |
| P(¬D) | 0.99 (99%) | No disease |
| P(T⁺|D) | 0.95 (95%) | Sensitivity — true positive rate |
| P(T⁻|¬D) | 0.95 (95%) | Specificity — true negative rate |
| P(T⁺|¬D) | 0.05 (5%) | False positive rate (1 − specificity) |

## Step 3: Apply Bayes' Theorem

Bayes theorem states:

```
P(D | T⁺) = P(T⁺ | D) × P(D) / P(T⁺)
```

We already have P(T⁺|D) and P(D). We need **P(T⁺)** — the total probability of a positive test.

## Step 4: Compute P(T⁺) — Total Probability Rule

A positive test can happen in two ways:
1. Person has disease AND test catches it: P(T⁺|D) × P(D)
2. Person is healthy AND test is wrong: P(T⁺|¬D) × P(¬D)

```
P(T⁺) = P(T⁺|D) × P(D) + P(T⁺|¬D) × P(¬D)

P(T⁺) = (0.95 × 0.01) + (0.05 × 0.99)
       = 0.0095 + 0.0495
       = 0.059
```

So **5.9%** of all tests come back positive.

## Step 5: Compute P(D|T⁺)

```
P(D | T⁺) = (0.95 × 0.01) / 0.059
           = 0.0095 / 0.059
           = 0.161016949...
           ≈ 0.161
```

## Step 6: Interpret the Result

```
P(D | T⁺) ≈ 16.1%
```

**Only ~16.1% of people who test positive actually have the disease.**

### Intuition

Despite the test being "95% accurate", a positive result is far from definitive. Why?

Because the disease is **rare** (1%). Even a 5% false positive rate produces many more false positives (4.95% of population) than true positives (0.95% of population):

| Outcome | Proportion of population | Fraction of positives |
|---------|------------------------|----------------------|
| True positive (have disease, test positive) | 0.95% | 16.1% |
| False positive (healthy, test positive) | 4.95% | 83.9% |
| **Total positive** | **5.9%** | **100%** |

The vast majority of positive tests are false positives simply because the disease is uncommon.

---

## General Formula

For any prevalence p, sensitivity α, and specificity β:

```
P(D | T⁺) = (α × p) / (α × p + (1 − β) × (1 − p))
```
