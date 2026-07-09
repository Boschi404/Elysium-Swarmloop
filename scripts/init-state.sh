#!/usr/bin/env bash
# ============================================================================
# init-state.sh — Elysium Swarmloop Bootloader
#
# Initialises the STATE object for the autonomous multi-agent orchestration
# engine.  Idempotent: re-run with the same GOAL to update state mid-loop.
#
# Usage:
#   ./init-state.sh                          # auto-detect goal from context
#   ./init-state.sh "Build a REST API"       # explicit goal
#   ./init-state.sh --json "Build a REST API" # raw JSON output only
# ============================================================================
set -euo pipefail

# ---- constants ---------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="${STATE_FILE:-${SCRIPT_DIR}/../.state.json}"
DEFAULT_SUBAGENTS=100
START_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ---- helpers -----------------------------------------------------------

# Print a usage message and exit.
usage() {
  cat <<EOF
Usage: $(basename "$0") [--json] [<goal>]

Options:
  --json    Print raw JSON state to stdout and exit (no side-effects).
  -h, --help  Show this message.

If <goal> is omitted the script tries to auto-detect it from the working
directory name or an existing STATE_FILE.
EOF
  exit 0
}

# ---- tier detection ----------------------------------------------------

# Auto-detect the execution tier based on task complexity keywords found in
# the goal string.  Uses a simple keyword-scoring heuristic.
#
# Returns: tier_number (1-4)
detect_tier() {
  local goal="$*"
  local score=0

  # Tier-1 signals (quick / trivial)
  if echo "$goal" | grep -qiE '\b(quick|tiny|minor|typo|config\s*change|edit|single\s*command|bump\s*version|rename)\b'; then
    score=1
  fi

  # Tier-2 signals (small feature / bugfix)
  if echo "$goal" | grep -qiE '\b(bugfix|bug\s*fix|feature|refactor|modular|test\s*add|small|update|patch|add\s*endpoint)\b'; then
    score=$(( score > 2 ? score : 2 ))
  fi

  # Tier-3 signals (multi-file / research)
  if echo "$goal" | grep -qiE '\b(api|research|migration|multi.?file|dashboard|integration|pipeline|service|module|component)\b'; then
    score=$(( score > 3 ? score : 3 ))
  fi

  # Tier-4 signals (greenfield / redesign)
  if echo "$goal" | grep -qiE '\b(greenfield|from\s*scratch|full.?stack|system|platform|redesign|rewrite|architecture|mvp|production)\b'; then
    score=$(( score > 4 ? score : 4 ))
  fi

  # Clamp 1-4
  if [[ $score -lt 1 ]]; then
    echo 1
  elif [[ $score -gt 4 ]]; then
    echo 4
  else
    echo "$score"
  fi
}

# Return the recommended subagent count for the given tier.
tier_to_subagents() {
  local tier="$1"
  case "$tier" in
    1) echo 3  ;;
    2) echo 10 ;;
    3) echo 35 ;;
    4) echo 80 ;;
    *) echo "$DEFAULT_SUBAGENTS" ;;
  esac
}

# Return the quality threshold (out of 10) for the given tier.
tier_to_threshold() {
  local tier="$1"
  case "$tier" in
    1) echo 6 ;;
    2) echo 7 ;;
    3) echo 7 ;;
    4) echo 8 ;;
    *) echo 7 ;;
  esac
}

# ---- state helpers -----------------------------------------------------

# Print the current state as a JSON object.
# Arguments: goal, tier, subagents, threshold, iteration, completed, failed,
#            in_flight, start_time
build_state_json() {
  local goal="$1"
  local tier="$2"
  local subagents="$3"
  local threshold="$4"
  local iteration="$5"
  local completed="$6"
  local failed="$7"
  local in_flight="$8"
  local start_time="$9"

  cat <<EOJSON
{
  "goal": $(echo "$goal" | jq -Rs .),
  "tier": $tier,
  "subagents": $subagents,
  "threshold": $threshold,
  "iteration": $iteration,
  "completed": $completed,
  "failed": $failed,
  "in_flight": $in_flight,
  "start_time": $(echo "$start_time" | jq -Rs .)
}
EOJSON
}

# Persist state JSON to STATE_FILE.
write_state() {
  echo "$1" > "$STATE_FILE"
  echo "[init-state] State written to $STATE_FILE" >&2
}

# Load state from STATE_FILE (if it exists) and source into environment.
# Prints JSON to stdout.
load_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE"
  else
    echo "{}"
  fi
}

# ---- assessment & decision helpers -------------------------------------

# Analyse current state and print a human-readable assessment.
# Reads state JSON from stdin.
assess_state() {
  local state
  state="$(cat)"

  local goal tier subagents threshold iteration completed failed in_flight
  goal="$(echo "$state" | jq -r '.goal // "unknown"')"
  tier="$(echo "$state" | jq -r '.tier // 1')"
  subagents="$(echo "$state" | jq -r '.subagents // 0')"
  threshold="$(echo "$state" | jq -r '.threshold // 6')"
  iteration="$(echo "$state" | jq -r '.iteration // 0')"
  completed="$(echo "$state" | jq -r '.completed // 0')"
  failed="$(echo "$state" | jq -r '.failed // 0')"
  in_flight="$(echo "$state" | jq -r '.in_flight // 0')"

  local total=$(( completed + failed + in_flight ))
  local pct=0
  if [[ $total -gt 0 ]]; then
    pct=$(( completed * 100 / total ))
  fi

  cat <<EOASSESS
═══ Elysium Swarmloop — State Assessment ═══
Goal:       ${goal}
Tier:       ${tier} (${subagents} subagents, threshold ${threshold}/10)
Iteration:  ${iteration}
Progress:   ${completed} done, ${failed} failed, ${in_flight} in flight
Pass rate:  ${pct}%
Status:     $( [[ $in_flight -gt 0 ]] && echo "IN FLIGHT — streaming" || [[ $failed -gt 0 ]] && echo "RETRY NEEDED" || [[ $completed -gt 0 ]] && echo "IDLE — check completion" || echo "NOT STARTED" )
══════════════════════════════════════════════
EOASSESS
}

# Based on current state, print the recommended next action.
# Reads state JSON from stdin.
decide_action() {
  local state
  state="$(cat)"

  local completed failed in_flight iteration max_iter
  completed="$(echo "$state" | jq -r '.completed // 0')"
  failed="$(echo "$state" | jq -r '.failed // 0')"
  in_flight="$(echo "$state" | jq -r '.in_flight // 0')"
  iteration="$(echo "$state" | jq -r '.iteration // 0')"
  max_iter="$(echo "$state" | jq -r '.max_iterations // 10')"

  if [[ $in_flight -gt 0 ]]; then
    echo '{"action": "stream", "reason": "Results in flight — wait and process streaming"}'
  elif [[ $failed -gt 0 ]] && [[ $iteration -lt $max_iter ]]; then
    echo '{"action": "retry", "reason": "Failed tasks exist — retry with enriched feedback"}'
  elif [[ $failed -gt 0 ]] && [[ $iteration -ge $max_iter ]]; then
    echo '{"action": "escalate", "reason": "Max iterations reached — escalate to user"}'
  elif [[ $completed -eq 0 ]] && [[ $in_flight -eq 0 ]]; then
    echo '{"action": "decompose", "reason": "Not started — decompose goal and dispatch"}'
  elif [[ $in_flight -eq 0 ]] && [[ $failed -eq 0 ]] && [[ $completed -gt 0 ]]; then
    echo '{"action": "complete", "reason": "All tasks accounted for — submit final report"}'
  else
    echo '{"action": "assess", "reason": "Ambiguous state — re-assess before deciding"}'
  fi
}

# Print the full state object in a human-friendly table.
# Reads state JSON from stdin.
print_state() {
  local state
  state="$(cat)"

  echo "$state" | jq -r '
    "╔══════════════════════════════════════╗",
    "║     Elysium Swarmloop — State        ║",
    "╠══════════════════════════════════════╣",
    "║ Goal:       " + (.goal // "—" | .[0:50]),
    "║ Tier:       " + (.tier | tostring) + "  (" + (.subagents | tostring) + " sub, threshold " + (.threshold | tostring) + "/10)",
    "║ Iteration:  " + (.iteration | tostring),
    "║ Completed:  " + (.completed | tostring),
    "║ Failed:     " + (.failed | tostring),
    "║ In flight:  " + (.in_flight | tostring),
    "║ Started:    " + (.start_time // "—"),
    "╚══════════════════════════════════════╝"
  '
}

# ---- main --------------------------------------------------------------

main() {
  local json_only=false
  local goal=""

  # Parse options
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --json)    json_only=true;  shift ;;
      -h|--help) usage ;;
      *)         goal="$*";       break ;;
    esac
  done

  # Auto-detect goal if not provided
  if [[ -z "$goal" ]]; then
    if [[ -f "$STATE_FILE" ]]; then
      goal="$(jq -r '.goal // empty' "$STATE_FILE" 2>/dev/null || true)"
    fi
    if [[ -z "$goal" ]]; then
      goal="$(basename "$(pwd)")"
    fi
  fi

  # Determine / increment state ------------------------------------------
  local existing_state
  existing_state="$(load_state)"

  local tier subagents threshold iteration completed failed in_flight start_time

  # Idempotent: if a state file exists AND goal matches, carry values forward
  local existing_goal
  existing_goal="$(echo "$existing_state" | jq -r '.goal // ""')"

  if [[ "$existing_goal" == "$goal" ]] && [[ "$existing_goal" != "" ]]; then
    # Re-use existing counters (idempotent update)
    tier="$(echo "$existing_state" | jq -r '.tier // 1')"
    subagents="$(echo "$existing_state" | jq -r '.subagents // 0')"
    threshold="$(echo "$existing_state" | jq -r '.threshold // 6')"
    iteration="$(echo "$existing_state" | jq -r '.iteration // 0')"
    completed="$(echo "$existing_state" | jq -r '.completed // 0')"
    failed="$(echo "$existing_state" | jq -r '.failed // 0')"
    in_flight="$(echo "$existing_state" | jq -r '.in_flight // 0')"
    start_time="$(echo "$existing_state" | jq -r '.start_time // ""')"
  else
    # Fresh initialisation
    tier="$(detect_tier "$goal")"
    subagents="$(tier_to_subagents "$tier")"
    threshold="$(tier_to_threshold "$tier")"
    iteration=0
    completed=0
    failed=0
    in_flight=0
    start_time="$START_TIME"
  fi

  # Build state JSON -----------------------------------------------------
  local state_json
  state_json="$(build_state_json \
    "$goal" "$tier" "$subagents" "$threshold" \
    "$iteration" "$completed" "$failed" "$in_flight" "$start_time")"

  # Output ------------------------------------------------------------------
  if $json_only; then
    echo "$state_json"
  else
    write_state "$state_json"
    echo "$state_json" | print_state
    echo ""
    echo "$state_json" | assess_state
    echo ""
    echo "Recommended action:"
    echo "$state_json" | decide_action
  fi
}

main "$@"
