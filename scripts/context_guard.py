#!/usr/bin/env python
"""
context_guard.py — Elysium Swarmloop Phase 3d can_dispatch() (v0.16.1)

Estimates the context cost of a dispatch batch and returns a recommendation
with confidence — NOT a bare boolean. One hard rule is non-negotiable:
est_context_tokens > budget_tokens * 0.8 → can_dispatch = false regardless
of confidence.

Usage:
    python context_guard.py --subagents 40 --tier 3 [--budget 128000] [--json]
    python context_guard.py --summary-tokens 800 --subagents 40 --budget 128000

Defaults follow Phase 3d: summary caps Tier 2 <500, Tier 3 <1000, Tier 4 <2000;
wave size 20; saturation threshold 0.8 (hard), caution band 0.6–0.8.
"""
from __future__ import annotations
import argparse, json, sys

SUMMARY_CAPS = {1: 400, 2: 500, 3: 1000, 4: 2000}
WAVE_SIZE = 20
HARD_FACTOR = 0.8   # can_dispatch=false above this — no exceptions
CAUTION_FACTOR = 0.6  # confidence starts degrading between 0.6 and 0.8


def estimate(n_subagents: int, summary_tokens: int) -> int:
    """Context cost estimate: each result summary plus per-task overhead."""
    per_task = summary_tokens + 150  # status/score/gaps/files metadata overhead
    return n_subagents * per_task


def guard(n_subagents: int, summary_tokens: int, budget_tokens: int) -> dict:
    est = estimate(n_subagents, summary_tokens)
    ratio = est / budget_tokens if budget_tokens > 0 else float('inf')

    if ratio > HARD_FACTOR:
        can_dispatch = False
        confidence = 0.95
        recommendation = 'REDUCE batch: split into waves or fewer subagents (hard rule).'
    elif ratio > CAUTION_FACTOR:
        can_dispatch = True
        # linear confidence decay 0.8→0.6 ratio band: 0.7 → 0.35
        confidence = round(0.7 - (ratio - CAUTION_FACTOR), 2)
        recommendation = f'CAUTION: use waves of {WAVE_SIZE} and compress summaries.'
    else:
        can_dispatch = True
        confidence = round(1.0 - ratio, 2)
        recommendation = 'OK: dispatch full batch.'

    diagnostics = {
        'n_subagents': n_subagents,
        'summary_tokens_cap': summary_tokens,
        'est_context_tokens': est,
        'budget_tokens': budget_tokens,
        'budget_ratio': round(ratio, 2),
        'saturation_risk': ('high' if ratio > HARD_FACTOR
                            else 'medium' if ratio > CAUTION_FACTOR else 'low'),
    }
    return {
        'can_dispatch': can_dispatch,
        'confidence': max(0.0, min(1.0, confidence)),
        'diagnostics': diagnostics,
        'suggested_wave_size': WAVE_SIZE,
        'hard_rule': f'can_dispatch=false if est_context_tokens > budget_tokens * {HARD_FACTOR}',
        'recommendation': recommendation,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='Elysium Phase 3d can_dispatch() gate.')
    ap.add_argument('--subagents', type=int, required=True)
    ap.add_argument('--tier', type=int, choices=[1, 2, 3, 4], default=None,
                    help='Tier → default summary cap (2:500, 3:1000, 4:2000).')
    ap.add_argument('--summary-tokens', type=int, default=None,
                    help='Explicit summary cap (overrides --tier).')
    ap.add_argument('--budget', type=int, default=128000,
                    help='Context budget in tokens (default 128000).')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    if args.summary_tokens is not None:
        cap = args.summary_tokens
    elif args.tier is not None:
        cap = SUMMARY_CAPS[args.tier]
    else:
        print(json.dumps({'error': 'provide --tier or --summary-tokens'}))
        return 2

    if args.subagents < 1 or cap < 1 or args.budget < 1:
        print(json.dumps({'error': 'values must be >= 1'}))
        return 2

    result = guard(args.subagents, cap, args.budget)
    print(json.dumps(result, indent=2 if args.json else None))
    return 0 if result['can_dispatch'] else 1


if __name__ == '__main__':
    sys.exit(main())
