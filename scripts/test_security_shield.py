#!/usr/bin/env python
"""
test_security_shield.py — smoke tests for security_shield.py
Run:  python test_security_shield.py
"""
import json, pathlib, subprocess, sys, tempfile

SCRIPT = pathlib.Path(__file__).parent / 'security_shield.py'


def run(args):
    r = subprocess.run([sys.executable, str(SCRIPT)] + args, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def tmp(content: str) -> str:
    d = tempfile.mkdtemp()
    f = pathlib.Path(d) / 'sample.py'
    f.write_text(content)
    return str(f)


def test_hardcoded_secret_blocked():
    code, out = run([tmp("API_KEY = 'sk-abc123456789'\n"), '--json'])
    assert code == 1, out


def test_env_secret_ok():
    code, out = run([tmp("import os\nAPI_KEY = os.getenv('API_KEY')\n"), '--json'])
    assert code == 0, out


def test_sql_fstring_blocked():
    code, out = run([tmp('uid = 1\nq = f"SELECT * FROM users WHERE id={uid}"\n'), '--json'])
    assert code == 1, out


def test_parameterized_ok():
    code, out = run([tmp('q = "SELECT * FROM users WHERE id=?"\n'), '--json'])
    assert code == 0, out


def test_pydantic_dict_blocked():
    code, out = run([tmp("from pydantic import BaseModel\nclass U(BaseModel):\n    x: int\nu = U(x=1)\nprint(u.dict())\n"), '--json'])
    assert code == 1, out


def test_http_json_not_flagged():
    code, out = run([tmp("import requests\nr = requests.get('http://x')\nprint(r.json())\n"), '--json'])
    assert code == 0, out


def test_tests_dir_excluded_for_fields():
    d = tempfile.mkdtemp()
    f = pathlib.Path(d) / 'test_x.py'
    f.write_text("assert hasattr(Model, '__fields__')\n")
    code, out = run([str(f), '--json'])
    assert code == 0, out


def test_cmd_blocked():
    code, out = run(['--check-command', 'rm -r' 'f /', '--json'])
    data = json.loads(out)
    assert data['verdict'] == 'blocked' and code == 1


def test_cmd_warn():
    code, out = run(['--check-command', 'rm -rf build/', '--json'])
    data = json.loads(out)
    assert data['verdict'] == 'warn' and code == 0


def test_cmd_allow():
    code, out = run(['--check-command', 'git status', '--json'])
    data = json.loads(out)
    assert data['verdict'] == 'allow' and code == 0


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
