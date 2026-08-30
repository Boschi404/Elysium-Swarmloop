#!/usr/bin/env python
"""
security_shield.py — Elysium Swarmloop Phase 3a (v0.16.1)

Materializes the 5 inline regex checks of Phase 3a into an executable gate.
Hermes's own approval system remains the final authority — this is a fast
pre-check, not a substitute.

Usage:
    python security_shield.py <file_or_dir>... [--json]
    python security_shield.py --check-command "rm -rf /" --json

Exit codes:
    0 = OK (no blocking violations)
    1 = blocking violations found (secrets / SQL injection / deprecated API)
    2 = usage error (e.g. --check-command with no command)

Checks:
    1. Hardcoded secrets (block) — env-safe assignment in next 3 lines is OK
    2. SQL injection risk via f-string/concat (block)
    3. Placeholder secrets (warn only)
    4. Deprecated APIs (block): __fields__, pydantic.v1, model .dict()/.json()
       Context-aware: .dict()/.json() flagged ONLY if the file imports pydantic
       AND the call is not an HTTP-client idiom (resp.json(), .to_dict(),
       .model_dump(), .json_sep...). Test files excluded entirely (check 4).
    5. Dangerous shell commands: --check-command mode →
       blocked | warn | allow (default-allow, per Phase 3a rule)
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys
from typing import List, Dict, Any

PY_EXT = {'.py'}
TEST_HINTS = ('test_', 'conftest', '/tests/', '\\tests\\')

# ── Check 1: hardcoded secrets ────────────────────────────────────────────────
RE_SECRET = re.compile(
    r"\b(api_key|password|secret|token|api_secret)\s*=\s*['\"][^'\"]{8,}",
    re.IGNORECASE
)
RE_ENV_SAFE = re.compile(r"os\.getenv|os\.environ|process\.env|get_secret|env\[", re.IGNORECASE)

# ── Check 2: SQL injection ────────────────────────────────────────────────────
RE_SQL_FSTRING = re.compile(r"f['\"](SELECT|INSERT|UPDATE|DELETE)\b", re.IGNORECASE)
RE_SQL_FORMAT = re.compile(r"\.format\(.*(?:SELECT|INSERT|UPDATE|DELETE)", re.IGNORECASE)
RE_SQL_CONCAT = re.compile(r"['\"]\s*\+\s*\w+\s*\+\s*['\"]\s*(?:SELECT|INSERT|UPDATE|DELETE)|(?:SELECT|INSERT|UPDATE|DELETE)\b[^'\"]*['\"]\s*\+\s*\w+", re.IGNORECASE)

# ── Check 3: placeholder secrets ──────────────────────────────────────────────
RE_PLACEHOLDER_SECRET = re.compile(
    r"\b(API_KEY|TOKEN|SECRET)\s*=\s*(['\"]\s*['\"]|None|''|\"\")\s*#\s*TODO",
    re.IGNORECASE
)

# ── Check 4: deprecated APIs ──────────────────────────────────────────────────
RE_FIELDS = re.compile(r"\.__fields__\b")
RE_PYDANTIC_V1 = re.compile(r"\bpydantic\.v1\b")
RE_PYDANTIC_IMPORT = re.compile(r"\b(import\s+pydantic|from\s+pydantic)\b")
RE_MODEL_DICT = re.compile(r"\.\bdict\(\)|\.\bjson\(\)")
# HTTP-client idioms / safe conversions — never flag these
RE_SAFE_CALLS = re.compile(
    r"\b(resp|response|request|req|reply|msg|message|payload|body|data|res)\w*\s*\.\s*(dict|json)\(\)"
    r"|\.\bto_dict\(\)|\.\bmodel_dump\(\)|\.\bmodel_dump_json\(\)"
    r"|\.\bjson\((indent|separators|sort_keys|default|cls)\s*=",
    re.IGNORECASE
)
RE_APP_ROUTE_OLD = re.compile(r"@app\.route\([^)]+\)\s*\n\s*def", re.MULTILINE)

# ── Check 5: dangerous shell commands ─────────────────────────────────────────
BLOCKED_CMD = [
    r"rm\s+-rf\s+/", r"chmod\s+777\s+/", r"dd\s+if=.*of=/dev/",
    r":\(\)\{\s*:\|:&\s*\};:", r">\s*/dev/sd[a-z]",
    r"mkfs\.", r">\s*/dev/null\s*<\s*/dev/",  # fork-bomb variants / disk smash
]
WARN_CMD = [
    r"rm\s+-rf\b", r"chmod\s+-R\s+777", r"curl[^|]*\|\s*(ba)?sh",
    r"\bwget[^|]*\|\s*(ba)?sh", r"\beval\b", r"\bsudo\b",
]

def _is_test_file(p: pathlib.Path) -> bool:
    s = str(p).replace('\\', '/')
    return any(h in s for h in ('/tests/', '/test_', 'conftest')) or p.name.startswith('test_')


def check_command(cmd: str) -> Dict[str, Any]:
    """Phase 3a check 5 — classify a shell command: allow | warn | blocked."""
    for pat in BLOCKED_CMD:
        if re.search(pat, cmd):
            return {'verdict': 'blocked', 'rule': f'blocked:{pat}',
                    'msg': 'Command blocked by security policy. Use safer alternative.'}
    for pat in WARN_CMD:
        if re.search(pat, cmd):
            return {'verdict': 'warn', 'rule': f'warn:{pat}',
                    'msg': 'Requires user confirmation (clarify) before execution.'}
    return {'verdict': 'allow', 'rule': None, 'msg': 'Default-allow (not default-deny).'}


def _scan_python(p: pathlib.Path) -> List[Dict[str, Any]]:
    v: List[Dict[str, Any]] = []
    try:
        src = p.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return [{'file': str(p), 'line': 0, 'check': 'read', 'severity': 'block', 'msg': str(e)}]

    is_test = _is_test_file(p)
    lines = src.splitlines()
    imports_pydantic = bool(RE_PYDANTIC_IMPORT.search(src))

    # 1 + 3: secrets (line-based so we can look at the next 3 lines)
    for i, line in enumerate(lines):
        if RE_SECRET.search(line):
            window = '\n'.join(lines[i + 1:i + 4])
            if not RE_ENV_SAFE.search(window):
                v.append({'file': str(p), 'line': i + 1, 'check': 'hardcoded_secret',
                          'severity': 'block',
                          'msg': 'Move credential to environment variable'})
        if RE_PLACEHOLDER_SECRET.search(line):
            v.append({'file': str(p), 'line': i + 1, 'check': 'placeholder_secret',
                      'severity': 'warn', 'msg': 'Placeholder secret (may be intentional)'})

    # 2: SQL injection
    for i, line in enumerate(lines):
        if RE_SQL_FSTRING.search(line) or RE_SQL_FORMAT.search(line) or RE_SQL_CONCAT.search(line):
            v.append({'file': str(p), 'line': i + 1, 'check': 'sql_injection',
                      'severity': 'block',
                      'msg': 'Use parameterized queries or ORM, never f-string SQL'})

    # 4: deprecated APIs — tests excluded (hasattr __fields__ is legit there)
    if not is_test:
        for i, line in enumerate(lines):
            if RE_FIELDS.search(line):
                v.append({'file': str(p), 'line': i + 1, 'check': 'deprecated_api',
                          'severity': 'block', 'msg': 'Pydantic v1 __fields__ — use model_fields'})
            if RE_PYDANTIC_V1.search(line):
                v.append({'file': str(p), 'line': i + 1, 'check': 'deprecated_api',
                          'severity': 'block', 'msg': 'pydantic.v1 import — migrate to pydantic v2'})
            if RE_APP_ROUTE_OLD.search(src):
                pass  # handled below (multiline)
            if imports_pydantic and RE_MODEL_DICT.search(line) and not RE_SAFE_CALLS.search(line):
                # confirm the target isn't an HTTP idiom by checking the var name too
                v.append({'file': str(p), 'line': i + 1, 'check': 'deprecated_api',
                          'severity': 'block',
                          'msg': 'model .dict()/.json() on pydantic — use .model_dump()/.model_dump_json()'})
        if RE_APP_ROUTE_OLD.search(src):
            m = RE_APP_ROUTE_OLD.search(src)
            v.append({'file': str(p), 'line': src[:m.start()].count('\n') + 1,
                      'check': 'deprecated_api', 'severity': 'block',
                      'msg': '@app.route without method decorator style — use FastAPI/Flask v2 patterns'})
    return v


def scan_paths(paths: List[str]) -> Dict[str, Any]:
    violations: List[Dict[str, Any]] = []
    for raw in paths:
        p = pathlib.Path(raw)
        if p.is_dir():
            for child in sorted(p.rglob('*')):
                if not child.is_file() or child.suffix not in PY_EXT:
                    continue
                if any(part in {'.git', '__pycache__', 'node_modules', '.venv'} for part in child.parts):
                    continue
                violations.extend(_scan_python(child))
        elif p.is_file() and p.suffix in PY_EXT:
            violations.extend(_scan_python(p))
    blocked = [x for x in violations if x['severity'] == 'block']
    return {'ok': len(blocked) == 0, 'violations': violations,
            'blocked_count': len(blocked), 'warn_count': len(violations) - len(blocked)}


def main() -> int:
    ap = argparse.ArgumentParser(description='Elysium Phase 3a security shield.')
    ap.add_argument('paths', nargs='*', help='Files or directories to scan (.py).')
    ap.add_argument('--check-command', dest='check_command', metavar='CMD',
                    help='Classify a shell command (check 5) instead of scanning files.')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    if args.check_command is not None:
        if not args.check_command.strip():
            print(json.dumps({'error': 'empty command'}, indent=2))
            return 2
        result = check_command(args.check_command)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['verdict'].upper()}  [{result['rule']}]  {result['msg']}")
        return 1 if result['verdict'] == 'blocked' else 0

    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2

    result = scan_paths(args.paths)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ OK ({result['warn_count']} warnings)" if result['ok']
              else f"❌ {result['blocked_count']} blocking ({result['warn_count']} warnings)")
        for v in result['violations']:
            print(f"  {v['severity'].upper():6} {v['file']}:{v['line']}  [{v['check']}]  {v['msg']}")
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
