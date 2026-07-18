"""
Bayes Theorem Solver — Disease Testing Problem
-----------------------------------------------
Given prevalence, sensitivity, and specificity, compute the posterior
probability P(disease | positive test) with full step-by-step output.
"""


def bayes_disease_test(
    prevalence: float = 0.01,
    sensitivity: float = 0.95,
    specificity: float = 0.95,
    verbose: bool = True,
) -> dict:
    """
    Compute P(disease | positive test) using Bayes Theorem.

    Parameters
    ----------
    prevalence : float
        P(D) — proportion of population with the disease (default 0.01)
    sensitivity : float
        P(T+ | D) — true positive rate (default 0.95)
    specificity : float
        P(T- | not D) — true negative rate (default 0.95)
    verbose : bool
        If True, print step-by-step derivation

    Returns
    -------
    dict with keys:
        p_disease_given_positive : float
        p_positive : float
        p_false_positive : float
        true_positive_rate : float
        false_positive_rate : float
        n_true_positives_per_10k : float
        n_false_positives_per_10k : float
    """
    p_d = prevalence
    p_not_d = 1.0 - prevalence
    p_t_given_d = sensitivity
    p_t_given_not_d = 1.0 - specificity  # false positive rate

    # Total probability of a positive test
    p_positive = p_t_given_d * p_d + p_t_given_not_d * p_not_d

    # Bayes theorem
    p_d_given_t = (p_t_given_d * p_d) / p_positive

    # Intuition (per 10,000)
    per_10k = 10_000
    tp = p_t_given_d * p_d * per_10k
    fp = p_t_given_not_d * p_not_d * per_10k

    if verbose:
        print("=" * 60)
        print(" BAYES THEOREM — DISEASE TESTING PROBLEM")
        print("=" * 60)
        print(f"\n  P(D)            = {p_d:<8.4f}  (prevalence)")
        print(f"  P(not D)        = {p_not_d:<8.4f}")
        print(f"  P(T+ | D)       = {p_t_given_d:<8.4f}  (sensitivity)")
        print(f"  P(T- | not D)   = {specificity:<8.4f}  (specificity)")
        print(f"  P(T+ | not D)   = {p_t_given_not_d:<8.4f}  (false positive rate)")
        print("\n  --- Numerator ---")
        print(f"  P(T+ | D) × P(D) = {p_t_given_d} × {p_d} = {p_t_given_d * p_d:.6f}")
        print("\n  --- Denominator: P(T+) ---")
        print(f"  = P(T+|D)P(D)  +  P(T+|not D)P(not D)")
        print(f"  = {p_t_given_d}×{p_d}  +  {p_t_given_not_d}×{p_not_d}")
        print(f"  = {p_t_given_d * p_d:.6f}  +  {p_t_given_not_d * p_not_d:.6f}")
        print(f"  = {p_positive:.6f}")
        print("\n  --- Bayes Theorem ---")
        print(f"  P(D | T+) = (P(T+|D) × P(D)) / P(T+)")
        print(f"           = {p_t_given_d} × {p_d} / {p_positive:.6f}")
        print(f"           = {p_t_given_d * p_d:.6f} / {p_positive:.6f}")
        print(f"           = {p_d_given_t:.6f}")
        print(f"           ≈ {p_d_given_t * 100:.1f}%")
        print()
        # Intuitive explanation
        per_10k = 10_000
        tp = p_t_given_d * p_d * per_10k
        fp = p_t_given_not_d * p_not_d * per_10k
        total_pos = tp + fp
        print("  --- Intuition (per 10,000 people) ---")
        print(f"  True positives:  {tp:.0f}  (have disease, test +)")
        print(f"  False positives: {fp:.0f}  (healthy, test +)")
        print(f"  Total positive:  {total_pos:.0f}")
        print(f"  P(disease | +) = {tp:.0f} / {total_pos:.0f} = {tp / total_pos:.1%}")
        print("=" * 60)

    return {
        "p_disease_given_positive": round(p_d_given_t, 6),
        "p_positive": round(p_positive, 6),
        "p_false_positive": round(p_t_given_not_d, 6),
        "true_positive_rate": round(p_t_given_d, 6),
        "false_positive_rate": round(p_t_given_not_d, 6),
        "n_true_positives_per_10k": round(tp, 1),
        "n_false_positives_per_10k": round(fp, 1),
    }


if __name__ == "__main__":
    result = bayes_disease_test()
    print()
    print(f"Result dict: {result}")
