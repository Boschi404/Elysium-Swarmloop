#!/usr/bin/env python
"""
test_context_guard.py — smoke tests for context_guard.py
Run:  python test_context_guard.py
"""
import importlib.util, pathlib, sys

spec = importlib.util.spec_from_file_location(
    'context_guard', pathlib.Path(__file__).parent / 'context_guard.py')
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


def test_small_batch_ok():
    r = cg.guard(10, 500, 128000)
    assert r['can_dispatch'] is True and r['confidence'] > 0.9


def test_tier3_default_cap():
    r = cg.guard(40, cg.SUMMARY_CAPS[3], 128000)
    assert r['diagnostics']['summary_tokens_cap'] == 1000


def test_hard_rule_blocks():
    # 100 subagents × (2000+150) = 215000 > 128000×0.8 → must block regardless
    r = cg.guard(100, cg.SUMMARY_CAPS[4], 128000)
    assert r['can_dispatch'] is False
    assert r['confidence'] >= 0.9, 'hard rule must carry high confidence'


def test_hard_rule_beats_confidence():
    # borderline math: even if confidence were low, hard rule forces false
    r = cg.guard(60, 2000, 128000)
    est = r['diagnostics']['est_context_tokens']
    assert est == 60 * 2150
    assert (est > 128000 * 0.8) == (r['can_dispatch'] is False)


def test_caution_band():
    # 40 × (1000+150) = 46000 → ratio 0.36 → OK
    r = cg.guard(40, 1000, 128000)
    assert r['diagnostics']['saturation_risk'] == 'low'
    # 80 × (1000+150) = 92000 → ratio 0.72 → caution
    r2 = cg.guard(80, 1000, 128000)
    assert r2['can_dispatch'] is True
    assert r2['diagnostics']['saturation_risk'] == 'medium'
    assert 0 < r2['confidence'] < 0.7


def test_wave_size_present():
    r = cg.guard(25, 500, 128000)
    assert r['suggested_wave_size'] == 20


def test_zero_budget_blocks():
    r = cg.guard(10, 500, 0)
    assert r['can_dispatch'] is False


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
    print(f"\n{len(tests)-failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
