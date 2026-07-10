"""
Elysium Swarmloop — Session Manager
Long session management: state tracking, checkpoint, quality trend, interrupt recovery.
Inspired by Prometheus Engine Phase 11.

Usage:
    from session_manager import SessionManager

    sm = SessionManager("build_auth", "Implement complete JWT auth")
    sm.track_turn(action="created User model", files=["models.py"], score=8)
    sm.track_decision("Use JWT refresh rotation", "More secure for mobile")
    if sm.should_checkpoint():
        sm.checkpoint()
    recovery = sm.recover()  # on interrupt
    summary = sm.get_context_summary()  # compact state for prompt
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


class SessionManager:
    """Manages long Hermes sessions with state persistence, checkpoints,
    quality trend monitoring, and interrupt recovery."""

    def __init__(self, session_id: str, goal: str, session_dir: str = None):
        self.session_id = session_id
        self.goal = goal
        self._turns: list[dict] = []
        self._decisions: list[dict] = []
        self._quality_scores: list[float] = []
        self._checkpoint_turns: list[int] = []
        self._start_time = time.time()
        self._last_checkpoint_time = time.time()

        if session_dir is None:
            hermes_home = Path.home() / ".hermes"
            self._session_dir = hermes_home / "sessions"
        else:
            self._session_dir = Path(session_dir)

        self._session_dir.mkdir(parents=True, exist_ok=True)

        # Try to recover on init
        self._recovered = self._try_recover()

    # --- Public API ---

    def track_turn(self, action: str, files: list[str] = None,
                   score: float = None, notes: str = None):
        """Record a completed turn."""
        turn = {
            "turn": len(self._turns) + 1,
            "action": action,
            "files": files or [],
            "score": score,
            "notes": notes or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._turns.append(turn)
        if score is not None:
            self._quality_scores.append(score)
        self._save_state()

    def track_decision(self, decision: str, rationale: str):
        """Record an architectural decision."""
        entry = {
            "turn": len(self._turns) + 1,
            "decision": decision,
            "rationale": rationale,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._decisions.append(entry)
        self._save_state()

    def should_checkpoint(self, turn_interval: int = 8,
                          time_interval: float = 600) -> bool:
        """Check if a checkpoint is needed."""
        if len(self._turns) == 0:
            return False
        last_cp_turn = self._checkpoint_turns[-1] if self._checkpoint_turns else 0
        turns_since = len(self._turns) - last_cp_turn
        time_since = time.time() - self._last_checkpoint_time
        return turns_since >= turn_interval or time_since >= time_interval

    def checkpoint(self) -> dict:
        """Create a checkpoint: compress old turns, save summary."""
        cp = {
            "turn": len(self._turns),
            "checkpoint_num": len(self._checkpoint_turns) + 1,
            "quality": self._get_quality_trend(),
            "total_turns": len(self._turns),
            "total_decisions": len(self._decisions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._checkpoint_turns.append(len(self._turns))
        self._last_checkpoint_time = time.time()

        # Save checkpoint
        cp_path = self._build_path(f"checkpoint_{cp['checkpoint_num']}.json")
        with open(cp_path, "w") as f:
            json.dump(cp, f, indent=2)

        # Keep only last 3 detailed turns, compress older ones
        if len(self._turns) > 3:
            compressed = []
            for t in self._turns[:-3]:
                compressed.append({
                    "turn": t["turn"],
                    "action": t["action"],
                    "score": t.get("score"),
                })
            # Save compressed archive
            archive_path = self._build_path(
                f"archive_{cp['checkpoint_num']}.json")
            with open(archive_path, "w") as f:
                json.dump(compressed, f, indent=2)

        return cp

    def recover(self) -> dict:
        """Try to recover a session after interrupt."""
        if self._recovered:
            return self._get_recovery_data()
        return {"status": "no_data", "message": "No prior session found"}

    def get_context_summary(self, max_turns: int = 3) -> str:
        """Generate compact summary for prompt (instead of full history)."""
        trend = self._get_quality_trend()
        recent = self._turns[-max_turns:] if self._turns else []
        files = set()
        for t in recent:
            files.update(t.get("files", []))

        lines = [
            f"=== SESSION STATE: {self.session_id} ===",
            f"Goal: {self.goal}",
            f"Turns completed: {len(self._turns)}",
            f"Average quality: {self._get_avg_quality():.1f}/10 ({trend})",
        ]
        if files:
            lines.append(f"Files modified: {', '.join(sorted(files)[:8])}")
        if self._decisions:
            lines.append(f"Architectural decisions: {len(self._decisions)}")
            for d in self._decisions[-2:]:
                lines.append(f"  - [{d['turn']}] {d['decision']}")
        if self._checkpoint_turns:
            lines.append(f"Last checkpoint: turn {self._checkpoint_turns[-1]}")
        if trend == "degrading":
            lines.append("⚠️ Quality is degrading — simplify next tasks.")

        return "\n".join(lines)

    # --- Internal ---

    def _get_avg_quality(self) -> float:
        if not self._quality_scores:
            return 0.0
        return mean(self._quality_scores)

    def _get_quality_trend(self) -> str:
        """Check if quality is stable, improving, or degrading."""
        if len(self._quality_scores) < 5:
            return "stable"
        recent = mean(self._quality_scores[-5:])
        older = mean(self._quality_scores[-10:-5]) if len(
            self._quality_scores) >= 10 else recent
        delta = recent - older
        if delta > 0.3:
            return "improving"
        elif delta < -0.3:
            return "degrading"
        return "stable"

    def _build_path(self, suffix: str) -> Path:
        return self._session_dir / f"{self.session_id}_{suffix}"

    def _state_path(self) -> Path:
        return self._build_path("state.json")

    def _save_state(self):
        state = {
            "session_id": self.session_id,
            "goal": self.goal,
            "start_time": self._start_time,
            "total_turns": len(self._turns),
            "total_decisions": len(self._decisions),
            "avg_quality": self._get_avg_quality(),
            "trend": self._get_quality_trend(),
            "checkpoints": self._checkpoint_turns,
            "last_update": time.time(),
        }
        with open(self._state_path(), "w") as f:
            json.dump(state, f, indent=2)

    def _try_recover(self) -> bool:
        """Try to load previous state."""
        state_path = self._state_path()
        if not state_path.exists():
            return False
        try:
            with open(state_path) as f:
                state = json.load(f)
            # Load last 3 turns from archive if available
            last_cp = state.get("checkpoints", [])
            if last_cp:
                archive = self._build_path(
                    f"archive_{len(last_cp)}.json")
                if archive.exists():
                    with open(archive) as f:
                        self._turns = json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def _get_recovery_data(self) -> dict:
        last_action = self._turns[-1] if self._turns else {}
        return {
            "status": "recovered",
            "total_turns": len(self._turns),
            "avg_quality": self._get_avg_quality(),
            "trend": self._get_quality_trend(),
            "last_action": last_action.get("action", ""),
            "last_score": last_action.get("score"),
            "files_created": list(set(
                f for t in self._turns for f in t.get("files", []))),
            "suggestion": (
                f"You were at turn {last_action.get('turn', '?')}: "
                f"'{last_action.get('action', '?')}'. Continue with..."
                if last_action else "Start fresh."
            ),
        }


# --- CLI usage ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <session_id> [goal]")
        sys.exit(1)

    sid = sys.argv[1]
    goal = sys.argv[2] if len(sys.argv) > 2 else "Session"
    sm = SessionManager(sid, goal)
    recovery = sm.recover()
    if recovery["status"] == "recovered":
        print(json.dumps(recovery, indent=2))
    else:
        print(f"New session: {sid}")
        print(sm.get_context_summary())
