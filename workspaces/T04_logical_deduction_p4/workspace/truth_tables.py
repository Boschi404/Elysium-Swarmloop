#!/usr/bin/env python3
"""
T04_logical_deduction — Truth Table Construction
=================================================
Two parts:
  A) Prove (P → Q) ∧ (Q → R) → (P → R) is a tautology.
  B) Test equivalence of (P → Q) ∧ (¬P → R)  ≡  (P ∧ Q) ∨ (¬P ∧ R).
"""

import itertools

# ── Helpers ──────────────────────────────────────────────────────────────

def implies(a, b):
    """Material implication: a → b  (equivalent to ¬a ∨ b)."""
    return (not a) or b

def tautology_analysis(label, expression_fn, variables):
    """Build a full truth table for *expression_fn* and return verdict + rows."""
    rows = []
    all_true = True
    for values in itertools.product([True, False], repeat=len(variables)):
        env = dict(zip(variables, values))
        result = expression_fn(env)
        rows.append((env, result))
        if not result:
            all_true = False
    return rows, all_true


# ── PART A :  (P → Q) ∧ (Q → R) → (P → R)  ────────────────────────────

def expr_a(env):
    p, q, r = env["P"], env["Q"], env["R"]
    lhs = implies(p, q) and implies(q, r)
    rhs = implies(p, r)
    return implies(lhs, rhs)

# ── PART B : equivalence check ──────────────────────────────────────────

def expr_b_lhs(env):
    p, q, r = env["P"], env["Q"], env["R"]
    return implies(p, q) and implies(not p, r)

def expr_b_rhs(env):
    p, q, r = env["P"], env["Q"], env["R"]
    return (p and q) or (not p and r)

# ── Display ─────────────────────────────────────────────────────────────

HEADER_A = (
    "╔══════════════════════════════════════════════════════════════════════════╗\n"
    "║  PART A — Tautology proof:  (P→Q) ∧ (Q→R)  →  (P→R)                   ║\n"
    "╚══════════════════════════════════════════════════════════════════════════╝"
)

HEADER_B = (
    "\n"
    "╔══════════════════════════════════════════════════════════════════════════╗\n"
    "║  PART B — Equivalence:  (P→Q) ∧ (¬P→R)  ≡  (P∧Q) ∨ (¬P∧R)            ║\n"
    "╚══════════════════════════════════════════════════════════════════════════╝"
)

COLS_A = ["P", "Q", "R", "P→Q", "Q→R", "(P→Q)∧(Q→R)", "P→R", "→(P→R)"]
COLS_B = ["P", "Q", "R", "P→Q", "¬P", "¬P→R", "LHS", "P∧Q", "¬P∧R", "RHS", "LHS≡RHS?"]

def fmt_bool(v):
    return "T" if v else "F"

def print_table(vars_list, cols, data_rows):
    """Pretty-print a truth table."""
    lines = []
    # header
    sep = "│"
    hdr = sep + sep.join(f" {c:^10} " for c in cols) + sep
    ruler = "├" + "┼".join("─" * 12 for _ in cols) + "┤"
    top = "┌" + "┬".join("─" * 12 for _ in cols) + "┐"
    bot = "└" + "┴".join("─" * 12 for _ in cols) + "┘"
    lines.append(top)
    lines.append(hdr)
    lines.append(ruler)

    for env, vals in data_rows:
        row = sep
        for v in vars_list:
            row += f" {fmt_bool(env[v]):^10} " + sep
        for v in vals:
            row += f" {v:^10} " + sep
        lines.append(row)

    lines.append(bot)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

out = []

# ── PART A ──
out.append(HEADER_A)

rows_a, is_tautology = tautology_analysis("A", expr_a, ["P", "Q", "R"])

table_a = []
for env, res in rows_a:
    p, q, r = env["P"], env["Q"], env["R"]
    row = [
        fmt_bool(implies(p, q)),          # P→Q
        fmt_bool(implies(q, r)),          # Q→R
        fmt_bool(implies(p, q) and implies(q, r)),  # antecedent
        fmt_bool(implies(p, r)),          # P→R
        fmt_bool(res),                    # full formula
    ]
    table_a.append((env, row))

out.append(print_table(["P", "Q", "R"], COLS_A, table_a))

if is_tautology:
    out.append(
        "\n  ✅ VERDICT:  (P → Q) ∧ (Q → R)  →  (P → R)  is a TAUTOLOGY.\n"
        "     This is the hypothetical syllogism — a fundamental rule of inference.\n"
        "     Every row evaluates to True; the implication is valid in all models."
    )
else:
    out.append("\n  ❌ VERDICT: NOT a tautology (at least one row evaluates to False).")

# ── PART B ──
out.append(HEADER_B)

rows_b = []
all_equal = True
for values in itertools.product([True, False], repeat=3):
    env = {"P": values[0], "Q": values[1], "R": values[2]}
    lhs = expr_b_lhs(env)
    rhs = expr_b_rhs(env)
    eq = lhs == rhs
    if not eq:
        all_equal = False
    rows_b.append((env, [
        fmt_bool(implies(env["P"], env["Q"])),       # P→Q
        fmt_bool(not env["P"]),                       # ¬P
        fmt_bool(implies(not env["P"], env["R"])),    # ¬P→R
        fmt_bool(lhs),                                 # LHS
        fmt_bool(env["P"] and env["Q"]),               # P∧Q
        fmt_bool((not env["P"]) and env["R"]),         # ¬P∧R
        fmt_bool(rhs),                                 # RHS
        "✅" if eq else "❌",                           # ≡?
    ]))

out.append(print_table(["P", "Q", "R"], COLS_B, rows_b))

if all_equal:
    out.append(
        "\n  ✅ VERDICT: The two expressions are LOGICALLY EQUIVALENT.\n"
        "     (P → Q) ∧ (¬P → R)  ≡  (P ∧ Q) ∨ (¬P ∧ R)\n"
        "     All 8 rows match.  The LHS expands via material implication\n"
        "     and distribution to match the RHS exactly."
    )
else:
    out.append(
        "\n  ❌ VERDICT: NOT equivalent — at least one row differs."
    )

# ── Write output ──
report = "\n".join(out)
print(report)

# Save to file
output_path = "C:\\Users\\Admin\\Elysium-Swarmloop\\workspaces\\T04_logical_deduction_p4\\workspace\\truth_table_output.txt"
with open(output_path, "w") as f:
    f.write(report)
print(f"\n📄 Output saved to {output_path}")
