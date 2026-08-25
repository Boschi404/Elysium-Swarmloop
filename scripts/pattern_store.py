#!/usr/bin/env python3
"""pattern_store.py — Elysium Swarmloop Phase 4a materialization (v0.16.0).

Turns the gated pattern-capture flow from prose into executable code.

Storage:
  - JSON files next to SKILL.md (created by init-state.sh bootstrap):
      pattern_cache.json        -> stable patterns (passed held-out gate)
      rejected_patterns.json    -> patterns rejected for a goal_type/context
      pattern_candidates.json   -> candidate patterns awaiting validation
  - SQLite store (~/.hermes/hermes.db, schema references/pattern-store.sql):
      executions, decomposition_patterns, pitfalls, calibrations,
      rejected_patterns, pattern_candidates

Usage:
  python pattern_store.py record-execution '<json>'
  python pattern_store.py capture-candidate '<json>'     # goes through gates
  python pattern_store.py promote <candidate_id>         # after gate passes
  python pattern_store.py reject   <candidate_id> '<reason>'
  python pattern_store.py recall <goal_type> [tier]      # STABLE only + rejected check
  python pattern_store.py cleanup                        # guardrail #5

Exit codes: 0 ok, 2 usage, 3 storage error.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PATTERN_CACHE = SKILL_DIR / "pattern_cache.json"
REJECTED_JSON = SKILL_DIR / "rejected_patterns.json"
CANDIDATES_JSON = SKILL_DIR / "pattern_candidates.json"

# Guardrail #1/#5 caps
MAX_STABLE_ENTRIES = 20
MIN_FPR_KEEP = 0.60


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_list(path: Path, items: list) -> None:
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _db_path() -> Path:
    home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    return Path(home) / "hermes.db"


def _sqlite_exec(sql_path: Path | None = None) -> sqlite3.Connection:
    """Open hermes.db and make sure all pattern-store tables exist."""
    db = _db_path()
    conn = sqlite3.connect(str(db))
    if sql_path is None:
        sql_path = SKILL_DIR / "references" / "pattern-store.sql"
    try:
        if sql_path.exists():
            conn.executescript(sql_path.read_text(encoding="utf-8"))
            conn.commit()
    except sqlite3.Error:
        pass  # DB may be shared with other Hermes subsystems; tables may already exist
    return conn


# ---------------------------------------------------------------- commands --

def record_execution(payload: dict) -> dict:
    conn = _sqlite_exec()
    cur = conn.execute(
        "INSERT INTO executions (goal, goal_type, tier, total_tasks,"
        " first_pass_rate, avg_quality, convergence_iterations,"
        " decomposition_pattern, start_time, duration_seconds, lessons)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            payload.get("goal", ""),
            payload.get("goal_type", "unknown"),
            int(payload.get("tier", 2)),
            int(payload.get("total_tasks", 0)),
            float(payload.get("first_pass_rate", 0.0)),
            float(payload.get("avg_quality", 0.0)),
            int(payload.get("iteration_count", 1)),
            payload.get("decomposition_pattern", ""),
            payload.get("start_time", _now()),
            int(payload.get("duration_seconds", 0)),
            json.dumps(payload.get("lessons", []), ensure_ascii=False),
        ),
    )
    conn.commit()
    result = {"execution_id": cur.lastrowid}
    conn.close()
    return result


def capture_candidate(payload: dict) -> dict:
    """Gate step 1+2: build candidate, run REJECTED CHECK before storing."""
    goal_type = payload.get("goal_type", "unknown")
    context = payload.get("context", "")
    candidate = {
        "id": f"cand_{uuid.uuid4().hex[:10]}",
        "goal_type": goal_type,
        "tier": payload.get("tier"),
        "decomposition": payload.get("decomposition", ""),
        "fpr": payload.get("fpr", 0.0),
        "quality": payload.get("quality", 0.0),
        "context": context,
        "status": "candidate",
        "created_at": _now(),
    }
    # REJECTED CHECK (4a step 2): same goal_type AND same decomposition rejected?
    for r in _read_list(REJECTED_JSON):
        if r.get("goal_type") == goal_type and r.get("decomposition") == candidate["decomposition"]:
            return {"skipped": True, "accepted": False,
                    "reason": "pattern already rejected for this goal_type/context",
                    "rejected_id": r.get("id"),
                    "rejection_reason": r.get("reason")}
    cands = _read_list(CANDIDATES_JSON)
    cands.append(candidate)
    _write_list(CANDIDATES_JSON, cands)
    return {"accepted": True, "candidate_id": candidate["id"]}


def promote(candidate_id: str) -> int:
    """Gate step 3-4: held-out validation PASSED -> promote to stable cache."""
    cands = _read_list(CANDIDATES_JSON)
    kept, promoted = [], 0
    for c in cands:
        if c.get("id") == candidate_id and c.get("status") == "candidate":
            c["status"] = "stable"
            c["promoted_at"] = _now()
            stable = _read_list(PATTERN_CACHE)
            stable.append(c)
            _write_list(PATTERN_CACHE, stable[-MAX_STABLE_ENTRIES:])
            promoted += 1
        else:
            kept.append(c)
    _write_list(CANDIDATES_JSON, kept)
    return promoted


def reject(candidate_id: str, reason: str) -> int:
    """Gate step 3-4: held-out validation FAILED or manual rejection."""
    cands = _read_list(CANDIDATES_JSON)
    kept, rejected_n = [], 0
    for c in cands:
        if c.get("id") == candidate_id:
            entry = {
                "id": c.get("id"),
                "goal_type": c.get("goal_type"),
                "decomposition": c.get("decomposition", ""),
                "reason": reason,
                "rejected_at": _now(),
            }
            rej = _read_list(REJECTED_JSON)
            rej.append(entry)
            _write_list(REJECTED_JSON, rej)
            rejected_n += 1
        else:
            kept.append(c)
    _write_list(CANDIDATES_JSON, kept)
    return rejected_n


def recall(goal_type: str, tier=None) -> dict:
    """Phase 4c steps 2-3: consult STABLE cache only; surface rejections as
    negative feedback. Candidates are NEVER returned here."""
    matches = [
        p for p in _read_list(PATTERN_CACHE)
        if p.get("goal_type") == goal_type and p.get("status") == "stable"
    ]
    best = None
    if matches:
        # highest FPR wins; must clear the 0.70 bar to be usable as template
        best = max(matches, key=lambda p: p.get("fpr", 0.0))
        if best.get("fpr", 0.0) <= 0.70:
            best = None
    rejections = [
        r for r in _read_list(REJECTED_JSON)
        if r.get("goal_type") == goal_type
    ]
    out = {
        "template": best,
        "rejections": rejections[-3:] if rejections else [],
        "note": "use template only if FPR > 70%" if best is None else None,
    }
    if not best and not rejections:
        out["note"] = "no stable pattern; decompose fresh"
    return out


def cleanup() -> dict:
    """Guardrail #5: keep <= MAX_STABLE_ENTRIES; drop low-FPR repeats."""
    stable = _read_list(PATTERN_CACHE)
    by_type: dict = {}
    for p in stable:
        by_type.setdefault(p.get("goal_type"), []).append(p)
    kept = []
    dropped = 0
    for gtype, items in by_type.items():
        lows = [p for p in items if p.get("fpr", 0.0) < MIN_FPR_KEEP]
        if len(lows) >= 3:
            dropped += len(lows)
            continue  # delete whole goal_type: repeated low performance
        items.sort(key=lambda p: (p.get("fpr", 0.0), p.get("promoted_at", "")), reverse=True)
        take = items[: max(1, MAX_STABLE_ENTRIES // max(1, len(by_type)))]
        dropped += len(items) - len(take)
        kept.extend(take)
    kept.sort(key=lambda p: p.get("promoted_at", ""), reverse=True)
    _write_list(PATTERN_CACHE, kept[:MAX_STABLE_ENTRIES])
    return {"kept": min(len(kept), MAX_STABLE_ENTRIES), "dropped": dropped}


def main(argv: list) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    try:
        if cmd == "record-execution" and len(argv) >= 3:
            out = record_execution(json.loads(argv[2]))
        elif cmd == "capture-candidate" and len(argv) >= 3:
            out = capture_candidate(json.loads(argv[2]))
        elif cmd == "promote" and len(argv) >= 3:
            n = promote(argv[2])
            out = {"promoted": n} if n else {"promoted": 0, "error": "candidate not found"}
        elif cmd == "reject" and len(argv) >= 4:
            n = reject(argv[2], argv[3])
            out = {"rejected": n} if n else {"rejected": 0, "error": "candidate not found"}
        elif cmd == "recall" and len(argv) >= 3:
            out = recall(argv[2], argv[3] if len(argv) > 3 else None)
        elif cmd == "cleanup":
            out = cleanup()
        else:
            print(__doc__)
            return 2
        print(json.dumps(out, ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, sqlite3.Error, OSError) as exc:
        print(f"storage error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
