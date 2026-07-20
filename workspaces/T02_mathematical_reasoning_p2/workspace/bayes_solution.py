"""
T02_mathematical_reasoning — Bayes Theorem: Disease Testing

Problem:
  A disease affects 1% of the population.
  A test is 95% accurate (sensitivity AND specificity).
  If someone tests positive, what is the probability they actually have the disease?

Solution via Bayes' Theorem:
  P(D|T+) = P(T+|D) × P(D) / P(T+)
"""

# ── Given data ──────────────────────────────────────────────────────────────
P_D = 0.01        # Prior probability of having the disease (prevalence)
P_not_D = 0.99    # Prior probability of NOT having the disease

# Test accuracy
sensitivity = 0.95    # P(T+ |  D) — true positive rate
specificity = 0.95    # P(T- | ¬D) — true negative rate

# Derived: false positive rate
P_T_given_not_D = 1 - specificity  # P(T+ | ¬D)

# ── Step 1: Total probability of a positive test ────────────────────────────
# Law of Total Probability:
# P(T+) = P(T+|D)·P(D)  +  P(T+|¬D)·P(¬D)
P_T = sensitivity * P_D + P_T_given_not_D * P_not_D

print("=" * 60)
print("BAYES THEOREM — DISEASE TESTING PROBLEM")
print("=" * 60)
print(f"\nGiven:")
print(f"  P(D)         = {P_D}   (disease prevalence)")
print(f"  P(not D)     = {P_not_D}")
print(f"  Sensitivity  = {sensitivity}   P(T+|D)  — true positive rate")
print(f"  Specificity  = {specificity}   P(T-|not D)")
print(f"  False Pos    = {P_T_given_not_D}   P(T+|not D)")

print(f"\nStep 1 — Total probability of a positive test:")
print(f"  P(T+) = P(T+|D)·P(D)  +  P(T+|¬D)·P(¬D)")
print(f"       = {sensitivity} × {P_D}  +  {P_T_given_not_D} × {P_not_D}")
print(f"       = {sensitivity * P_D}  +  {P_T_given_not_D * P_not_D}")
print(f"       = {P_T}")

# ── Step 2: Apply Bayes' Theorem ───────────────────────────────────────────
# P(D|T+) = P(T+|D) × P(D) / P(T+)
P_D_given_T = sensitivity * P_D / P_T

print(f"\nStep 2 — Bayes' Theorem:")
print(f"  P(D|T+) = P(T+|D) × P(D) / P(T+)")
print(f"         = {sensitivity} × {P_D} / {P_T}")
print(f"         = {sensitivity * P_D} / {P_T}")

# ── Step 3: Result ─────────────────────────────────────────────────────────
print(f"\nResult:")
print(f"  P(D|T+) = {P_D_given_T}")
print(f"  ≈ {P_D_given_T:.3f}  ({P_D_given_T:.1%})")
print(f"\nInterpretation:")
print(f"  Even with a positive test, there is only about a {P_D_given_T:.0%} chance")
print(f"  of actually having the disease. The other ~{100 - round(P_D_given_T * 100)}% are")
print(f"  false positives caused by the disease's low prevalence (1%).")
print(f"\nIntuition check:")
print(f"  Out of 1000 people:")
n = 1000
sick = n * P_D
healthy = n * P_not_D
tp = sick * sensitivity
fp = healthy * P_T_given_not_D
print(f"    • {sick:.0f}  are sick     → {tp:.0f} test positive (true pos)")
print(f"    • {healthy:.0f} are healthy  → {fp:.0f} test positive (false pos)")
print(f"    • Total positive: {tp + fp:.0f}")
print(f"    • P(D|T+) = {tp:.0f}/{tp + fp:.0f} = {tp / (tp + fp):.3f}")

# ── Verify against expected value ──────────────────────────────────────────
expected = 0.161
computed = round(P_D_given_T, 3)
assert computed == expected, (
    f"MISMATCH: computed {computed}, expected {expected}"
)
print(f"\n✓ Verified: result matches expected value ({expected})\n")
