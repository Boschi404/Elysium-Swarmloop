---
name: elysium-swarmloop
description: "The Multi-Agent Orchestration Engine with self-learning mechanisms, automatic solution-space exploration, and self-updating bootstrap. v0.11.1: Auto-Update Bootstrap (git-based version check at every activation, install.sh git init)."
version: 0.11.1
author: Boschi404 + ffazecaldy
testing-agent: Hermes Agent
tags: [agentic, auto, workflow, multi-agent, quality, research, iteration, scatter-gather, streaming-gather, self-learning, autonomous-loop, meta-scaling, orchestrator-depth2, self-improving, swarmloop, guardrails, security-shield, context-protection, contracts, clarification, plan-integration, sandbox-racing, quality-first, e2e-tested, solution-exploration, trade-off-analysis, multi-strategy]
user_preferences:
  language: "italiano"
  auto_commit: true
  auto_push: true
  test_command: "pytest -q"
---
# Elysium Swarmloop
The Multi-Agent Orchestration Engine with self-learning mechanisms
*Towards Agentic Utopia.*

> ⚠️ **Nota di trasparenza (v0.9.0):** In v0.9.0 sono stati eseguiti test di falsificazione sullo scoring engine:
> - **CodeScoringEngine correctness**: ceiling effect CONFERMATO. 3 soluzioni rotte → correctness=0.0 (tests falliscono), 1 soluzione corretta → correctness=40.0 (tests passano). Il scorer funziona; il problema è che tutte le soluzioni benchmark passano tutti i test. Vedi `risultati/correctness_falsification_test/`.
> - **DataScoringEngine fix**: VERIFICATO 5/5 coppie (buona/scadente). Il fix al `_rubric_check` produce punteggi differenziati per completeness/efficiency/robustness/clarity. correctness resta 40.0 per entrambi (validate.py esce sempre con returncode=0). Vedi `risultati/dataengine_verification/`.
> - **Self-learning Δ**: non ancora ri-benchmarkato con scorer verificato. I claim di auto-miglioramento restano "non verificati" fino a un ri-benchmark con 6+ loop.

## Required Config (BEFORE FIRST USE)

These **Hermes config settings are mandatory**. Without them, the loop is castrated:

```yaml
delegation:
  max_concurrent_children: 100   # max parallelism (up to 100 subagents)
  max_async_children: 100        # same for async ops
  max_spawn_depth: 2             # orchestrators can spawn leaf workers
  child_timeout_seconds: 600     # generous timeout for complex tasks
  max_iterations: 50             # deep reasoning per agent
  orchestrator_enabled: true     # enable hierarchical orchestration
```

**Run these commands** (or edit `~/AppData/Local/hermes/config.yaml` directly):

```bash
hermes config set delegation.max_concurrent_children 100
hermes config set delegation.max_spawn_depth 2
hermes config set delegation.orchestrator_enabled true
hermes config set delegation.child_timeout_seconds 600
hermes config set approvals.mode smart
```

> **Why critical**: with defaults (3 subagents), Tier 4 tasks run at 3% of possible speed. The loop needs ALL 100 slots to reach full potential.

## Auto-Update Bootstrap (v0.10.1+)

This skill is **self-maintaining**. Every activation checks GitHub for a newer version.

### How it works

At session start, BEFORE the 4-Band Filter:

```
1. cd $SKILL_DIR && git fetch origin main 2>/dev/null
2. Compare LOCAL vs REMOTE commit hash
3. If REMOTE is ahead → notify user ONCE:
   "🔄 Elysium Swarmloop v{NEW} available (you're on v{OLD}).
    Run: cd $SKILL_DIR && git pull && /reload-skills"
4. Continue with CURRENT version (never auto-update without consent)
```

**Why not auto-update?** Guardrail #7 (Human Checkpoint): skill mutations require user consent. Even beneficial updates are structural changes — the user must opt in.

### Install (if not already a git repo)

```bash
cd ~/AppData/Local/hermes/skills/autonomous-agents/elysium-swarmloop
git init && git remote add origin https://github.com/Boschi404/Elysium-Swarmloop.git
git fetch origin && git reset --hard origin/main
```

After install, `git pull` is all you need to stay current. Then `/reload-skills`.

### Fresh install
```bash
bash scripts/install.sh   # sets up git automatically
```

## User Preferences

The loop reads these settings from the YAML frontmatter at every execution:

| Setting | Default | Effect |
|---------|---------|--------|
| `language` | `italiano` | Response language for all communication |
| `auto_commit` | `true` | Git commit after every passing task |
| `auto_push` | `true` | Git push after every commit |
| `test_command` | `pytest -q` | Command used for test execution |

Override any preference by editing the `user_preferences:` section at the top of this file.
**Language note**: when the user writes in a non-English language, all responses, subagent contexts, commit messages and final reports are in that language. If `language` is set, it overrides auto-detection.

## Philosophy

**I don't follow a workflow. I am the loop. And I improve myself.**

> ⚠️ Il claim "I improve myself" si riferisce al meccanismo di Phase 4 (pattern capture, recall, calibration). La sua efficacia quantitativa non è ancora verificata con scorer affidabili — self-learning Δ non ri-benchmarkato con 6+ loop. Vedi nota di trasparenza all'inizio del documento.

Elysium Swarmloop is a self-improving autonomous orchestration engine that:
1. \*\*Decides what to do next\*\* — state machine, not recipe
2. \*\*Executes at any scale\*\* — 1 to 100 subagents per batch
3. \*\*Orchestrates hierarchically\*\* — depth-2: orchestrators spawn workers (depth-3 with B1-B6 rules for complex tasks)
4. \*\*Evaluates and retries instantly\*\* — streaming gather, no batching delay
5. \*\*Learns and evolves\*\* — captures patterns, calibrates, bumps version on improvement
6. \*\*Validates at every layer\*\* — security, file integrity, execution, context budget
7. \*\*Protects itself\*\* — 10 guardrails prevent self-learning contamination
\*\*Guardrails for self-modification:\*\*
- Every edit to this skill must \*\*improve the autonomous workflow\*\*, not add project-specific trivia
- No project error messages, framework-specific bugs, or dependency issues
- Each modification increments the PATCH version (v0.7.x), meaningful improvements bump MINOR (v0.x), breakthrough rewrites bump MAJOR (v1.0.0)
- When version bumps, the skill's own `# Changelog` section at the bottom gets a new entry
---
### ⚖️ Precedence Rule — Policy Conflict Resolution
When two sections describe alternative policies for the same moment in the flow, \*\*the most restrictive wins\*\* (safety > autonomy). Order of precedence:
1. ⚖️ \*\*Precedence Rule\*\* (this section) — always active
2. 🛡️ \*\*Guardrails (Phase 4e)\*\* — protect the system from itself
3. 🪜 \*\*Escalation Ladder (Phase 3j)\*\* — user decides on below-threshold gaps
4. 🧠 \*\*Context Protection (Phase 3d)\*\* — prevents overflow/saturation
5. 🎯 \*\*4-Band Filter\*\* — pre-check before loading skill
6. ✨ \*\*Quality Gate (Phase 3)\*\* — evaluates and retries
7. 📡 \*\*Scatter (Phase 2)\*\* — parallel dispatch
\*\*Example:\*\* if Quality Gate says "accept task below threshold" but Escalation Ladder says "escalate to user" → Escalation wins. If Phase 2 says "dispatch 50 streaming" but Context Protection says "max 20-25 in-flight" → Context Protection wins.
---
### 🎯 4-Band Filter — First Checkpoint (BEFORE everything)

**BEFORE loading the rest of the skill**, categorize the request into 4 bands. This determines WHETHER to load the skill. Subagent numbers are in the Tier Auto-Detection table (Phase 0a) — this table is a pure on/off switch.

| Band | Examples | Load skill? | Loop? |
|------|----------|-------------|-------|
| **Low** | typo, fix bug, rename, single command | ❌ No (saves 8K tokens) | No, direct |
| **Medium** | add endpoint, create function, test, refactor | ✅ Yes | 1 iteration |
| **High** | system, auth module, full API, multi-file feature | ✅ Yes | ∞ converge |
| **Extreme** | full-stack, e-commerce, MVP from zero, 50+ files | ✅ Yes | ∞ + orchestrator |

**Token saving rule:**
```
IF band == "low":
└─ DON'T load SKILL.md (8K tokens saved)
└─ Execute directly: read, edit, commit, push
└─ No loop, no subagents, no plan
IF band == "medium":
└─ Load SKILL.md, fast path: decompose → dispatch → gather → done
└─ Max 1 retry, no self-learning
IF band == "high" or "extreme":
└─ Load full SKILL.md
└─ Full loop with all phases
└─ Self-learning active
```
**When in doubt, prefer the HIGHER band.** It's better to load the skill for a medium task and discover it was low, than to skip it for a high task.

#### 🔨 Hard Trigger Activation (bypass 4-Band Filter)

If the user explicitly includes these keywords in their goal, **the 4-Band Filter is bypassed** and the loop activates at Tier 2 minimum (never skipped):

| Trigger Keyword | Effect |
|----------------|--------|
| `"attiva elysium"`, `"modalità elysium"`, `"elysium mode"`, `"swarmloop"` | Bypass filter → force loop activation |
| `"massima qualità"`, `"maximum quality"`, `"quality-first"` | Bypass filter + activate Quality-First Mode (see Phase 0a) |

**Rule**: these keywords override band detection. Even a "Low" request like "fix typo" becomes Tier 2 if prefixed with "attiva elysium, fixa il typo".
---
## The Core Loop
```python
while goal_not_achieved:
    state = assess(goal, done, gaps)
    if state.is_done: break
    decide()        # what to do next based on state
    explore()       # (Tier 3+) multi-strategy exploration, pick best
    decompose()     # break winning approach into tasks
    scatter()       # dispatch all in parallel
    stream()        # process each result as it arrives
                    # immediate retry on failures
    learn()         # save patterns, calibrate, improve
```
---
## 🚀 Quick Start
GOAL: "Crea sistema di prenotazione ristorante"

1. STATE INIT → tier 3, 50 subagenti, soglia 7/10
2. EXPLORE → 3 strategy scout: monolith vs microservices vs layered. Winner: layered (score 8.2/10)
3. DECOMPOSE → 40 task atomici su 40 file diversi (layered approach)
4. SCATTER → dispatch 40 subagenti in parallelo
5. STREAM → processa streaming: 42 pass, 8 fail → retry immediati
6. CONVERGE → 3 iterazioni, 100% pass
7. LEARN → salva pattern "layered per api_crud" + "decomposizione per_file per CRUD"
8. REPORT → first-pass 84%, qualità 8.6/10, 5 minuti
```
---
## Phase 0 — Autonomous Loop Engine (ALWAYS ACTIVE)
### 0a — State

```python
STATE = {
    "goal": "", "tier": auto_detect(), "quality_threshold": tier_to_threshold(tier),
    "subagents_available": 100, "subagents_used": 0,
    "tasks_completed": [], "tasks_failed": [], "tasks_in_flight": [],
    "iteration": 0, "max_iterations": auto_calc(tier),
    "first_pass_rate": None, "avg_quality_score": None,
    "self_lessons": [], "codebase_familiarity": "unknown",
    "quality_first": False, "global_recheck": False,
    "clarify_mode": False, "plan_file": "", "start_time": now(),
}
```

**Tier Auto-Detection:**
| Tier | Subagents | Threshold | When |
|------|-----------|-----------|------|
| 1 | 1-3 | 6/10 | Single edit, 1 file, ≤2 keywords |
| 2 | 5-15 | 7/10 | 1-3 files, CRUD, < 1h |
| 3 | 15-50 | 7/10 | 3-10 files, auth+CRUD+services |
| 4 | 50-100 | 8/10 | 10+ files, greenfield, cross-system |

**Word-boundary matching:** `\bapi\b` not "api" inside "/api/users/". Single endpoint + model = Tier 2.
**Tier 1 Fast-Path:** ≤2 files + no deps = skip loop entirely, direct execution.

**Codebase Familiarity Override:**
| Knowledge | Adjustment |
|-----------|-----------|
| Never seen | Standard tier |
| Explored before | -50% subagents |
| Know by memory (5+ files) | -80% or 0 |
| Wrote the module | 0 subagents, direct |

**Quality-First Mode:** keywords "massima qualità"/"quality-first" → threshold 9/10, max_iterations 9, fine granularity, Global Re-Check enabled.

**State Initialization:** `bash scripts/init-state.sh "goal"` (or `--quality-first`, `--clarify`, `--plan-file`, `--structural-scan`, `--json`).
### 0b — Assess

```
ASSESS: (1) completed? (2) failed + gaps? (3) in-flight? (4) goal reachable? (5) adjust strategy? (6) past patterns? (7) tier correct?
```

### 0c — Decide

```
if in_flight → stream | elif failed & <max → retry | elif failed & >=max → escalate
elif not started → decompose | elif done & OK → COMPLETE | elif done & LOW → quality loop
```

---

## Phase 0.5a — Clarification Interview

Before decomposing (Tier 3+), ask 5-6 questions in one message:
1. DB: SQLite (default), PostgreSQL, or other?
2. Frontend: None (default), React, Vue?
3. Auth: JWT (default), session, or none?
4. Deploy: local (default), Docker, cloud?
5. Scope: MVP (default), complete, or production-ready?
6. Testing: minimal (default), comprehensive, or TDD?

User can answer inline or say "fai tu" to use defaults. 2 min of questions saves 20+ min of wrong-assumption retries.

---
## Phase 0.5b — Plan Integration

Before dispatching (Tier 3+), write plan to `.hermes/plans/{goal_type}/{date}.md`:
- File manifest: exact files to create/modify
- Dependencies: build order
- Interface contracts: function signatures between modules
- Task assignments: which subagent works on what

Without a plan file, two subagents can modify the same `__init__.py` → conflicts.

---
## Phase 0.5c — Structural Alignment

If project exists (not greenfield), scan before creating files:
```
1. ls -R <path> | head -50    (directory structure)
2. Find *.py and check naming conventions
3. Find package.json/pyproject.toml (tech stack)
4. Inject conventions as quality criteria in every subagent
```
New code matches existing code style. No "why is this file here" surprises.

---

## Phase 0.6 — Solution-Space Exploration (Tier 3+ AUTO)

**Activation:** automatic for ALL Tier 3+ tasks. Not gated behind keywords or retry failures. Goal: find the best architectural approach BEFORE committing 50 subagents to one path.

### 0.6a — Strategy Generation

Spawn 3 "strategy scouts" (leaf, fast-tracked) in parallel. Each proposes ONE distinct architectural approach:

```
SCOUT PROMPT:
You are a strategy scout. Given: "{goal}"
Propose ONE architectural approach. Do NOT implement.
Return STRUCTURED JSON:
{
  "approach": "<name>",
  "architecture": "<2-3 sentence description>",
  "key_decisions": ["<d1>", "<d2>", "<d3>"],
  "pros": ["<pro1>", "<pro2>", "<pro3>"],
  "cons": ["<con1>", "<con2>", "<con3>"],
  "complexity": <1-10>,
  "risk": <1-10>,
  "estimated_subagents": <N>,
  "approach_type": "monolith|microservices|pipeline|plugin|layered|event-driven|other"
}
```

**Scout biases (one per scout):** "prefer simplicity", "prefer scalability", "prefer speed of implementation". Each scout gets ONE bias — ensures genuinely different approaches, not 3 copies of the same idea.

**Rules:** LEAF (cannot spawn further). Timeout: 120s each. Invalid JSON → use remaining scouts. ≤ 2 scouts available → skip exploration, proceed to Phase 1 directly (not enough signal).

### 0.6b — Trade-off Matrix

Compare all valid scout proposals on 5 weighted axes:

| Axis | Weight | Meaning |
|------|:------:|---------|
| **Quality** | ×2.0 | Correctness, edge cases, robustness |
| **Maintainability** | ×1.5 | Future changes, readability, modularity |
| **Speed** | ×1.0 | Time to implement (lower subagent count = faster) |
| **Scalability** | ×1.0 | Growth capacity, performance under load |
| **Risk** | −1.5 | Dependencies, unknowns, integration complexity |

**Weighted Score:** quality×2.0 + maintainability×1.5 + speed×1.0 + scalability×1.0 − risk×1.5

### 0.6c — Winner Selection

```
1. Compute weighted score for each scout
2. Winner = highest weighted score
3. DOCUMENT: "Selected {approach} (score {X}) over {runner_up} (score {Y}). Reason: {top discriminating factor}."
4. Save to plan file (Phase 0.5b): which approach chosen and why
```

**Anti-bias check:** if winner wins ONLY because of speed (speed dominates the score but quality is low) → re-evaluate with quality weight ×3.0. Fast-but-fragile loses to slower-but-solid.

### 0.6d — Synthesis (if top 2 within 15%)

If 2nd place score ≥ 85% of winner score → spawn 1 synthesis agent:

```
Goal: "Combine the best elements of approach A ({winner}) and approach B ({runner_up}).
       Use A's architecture as base, incorporate B's best distinguishing idea."
Result: hybrid approach → re-run 0.6a-0.6c cycle on the hybrid (max 1 retry).
```

### 0.6e — Hand-off to Decomposition

Pass the WINNING APPROACH to Phase 1, not the raw goal:

```
Phase 1 receives:
  goal: "{original_goal}"
  approach: "{winning_approach_name} — {architecture summary}"
  key_decisions: [{d1}, {d2}, {d3}]
  approach_type: "{type}"
```

Phase 1 decomposes the STRATEGY into tasks — not the abstract goal.

### 0.6f — Pattern Capture

Save which approach types win for which goal types:

| Goal Type | → Wins | Skip next time? |
|-----------|--------|:---:|
| api_creation → layered | 3+ times | ✅ Skip exploration, use layered directly |

**Learning:** if approach_type X wins 3+ times for goal_type Y → skip Phase 0.6 next time, inject X directly into Phase 1. Saves 3 scout subagents per repeat.

---

## Phase 1 — Task Decomposition
### 1a — Dynamic Granularity
Decomposition adapts to available subagents:
| Subagents | Granularity |
|-----------|-------------|
| 1-5 | Per-file (model.py, routes.py, services.py) |
| 5-15 | Per-function (each endpoint, each test suite) |
| 15-50 | Per-component (User model, Auth routes, Validation) |
| 50-100 | Per-line + multi-variant (3 implementations, pick best) |
```python
def decompose(goal, available, iteration):
if iteration == 0: return fine\_grained(goal, count=available \* 0.8)
else: return fine\_grained(gaps, count=len(gaps) \* 3)
```
### 1b — Scale Patterns

| Pattern | Subagents | When |
|---------|-----------|------|
| Micro-Task Cascade | 50-100 | Big project, one file per task |
| Multi-Variant + Selection | 30-50 | Critical component, pick best |
| Research → Implement → Test | 50-100 | Need research first |
| Full System Build | 80-100 | Greenfield full-stack MVP |
| Data Pipeline | 50-100 | Multi-source ETL, transform, merge |
### 1c — Clean Code Standards (by Tier)
**Do NOT apply to Tier 1** (quick fixes) or **non-code tasks** (logical deduction, security analysis). For Tier 2-4 code tasks, these are **mandatory** in subagent quality criteria:

```
CLEAN CODE STANDARDS (injected into quality criteria — CODE TASKS ONLY):

1. TYPE HINTS & DOCSTRINGS (Tier 2-4 code):
   ├─ Every function must have explicit type hints (params + return)
   ├─ Every public function must have a concise docstring
   └─ Validation phase checks type hint presence

2. SINGLE RESPONSIBILITY (Tier 3-4, via Actor-Critic):
   ├─ One function/class does ONE thing
   ├─ If an API route does DB query + business logic + email → ❌ FAILED
   └─ Verified by Actor-Critic, not automatic regex

3. DRY (Tier 3-4, via Assembly Task):
   ├─ If two subagents produce duplicate code, extract to shared module
   └─ Verified by Assembly Task (Phase 3g point 6)

4. ERROR HANDLING (Tier 2-4 code):
   ├─ External calls (DB, API, filesystem, network) MUST have error handling
   ├─ FastAPI: `raise HTTPException(status_code=...)` counts as error handling (idiomatic pattern)
   ├─ Generic: `try/except Exception as e` counts
   ├─ Bare `except:` without Exception class → ❌ FAILED
   └─ Verified by Phase 3b check 5

5. FILTER: skip ALL checks if task_type is NOT code
   └─ text/analysis tasks (logical_deduction, code_review, security_analysis) → skip Phase 1c
```
### 1d — Shared Interface Contracts (pre-dispatch)

If subagent A calls functions from subagent B, document exact signatures in BOTH contexts:
```
--- INTERFACE CONTRACT ---
Called: app/client.py — build_prompt(location: GeoResult, target_date: date) -> str (SYNC)
Caller: app/router.py — from client import build_prompt; result = build_prompt(loc, d)
--- END CONTRACT ---
```
Eliminates 90% of integration bugs. If Batch 1 already started, Batch 2 adapts to its signatures.

### 1e — Dynamic Quality Criteria

```python
criteria = {"completeness", "correctness", "edge_cases"}
if task_type == "api": criteria += {"status_codes", "validation", "tests"}
if task_type == "model": criteria += {"constraints", "repr", "migration"}
if task_type == "ui": criteria += {"responsive", "states", "anti-slop"}
```
---
## Phase 2 — Hierarchical Scatter (Depth-2/3 Orchestration)
### 2a — Two-Level Hierarchy (+ B1-B6 Anti-Bottleneck)
With `max\_spawn\_depth: 2`, subagents can be orchestrators that spawn their own workers:
```
MAIN AGENT
└── delegate\_task(role="orchestrator", goal="Analizza e fixa modulo X")
├── worker "trova bug" (leaf, default)
├── worker "trova vulnerabilità" (leaf)
└── worker "propone fix" (leaf)
```
\*\*Rules:\*\*
- `role="orchestrator"` → subagent can use `delegate\_task(tasks=[...])` with leaf workers
- `role="leaf"` (default) → cannot delegate further
- Orchestrator collects worker results, synthesizes, returns summary
- Workers are always leaves at depth 2
\*\*For Tier 4 (Epic, 50+ files) — Depth-3 with B1-B6 Anti-Bottleneck Rules:\*\*
For very complex tasks, use 3-level hierarchy: Parent → Orchestrator → Leaf → Micro-worker.
\*\*6 Anti-Bottleneck Rules (B1-B6):\*\*
```
B1 — Mini-batch: max 5 leaf workers per orchestrator batch (not all at once)
B2 — Depth auto-limit by Tier: T1-2→1 level, T3→2 levels, T4→3 levels (only if >50 files)
B3 — Context snapshot: <200 token snapshot injected into every subagent
B4 — Retry degradation: retry 2 = inline by leaf, retry 3 = orchestrator does it inline
B5 — Aligned timeouts: micro 60s → leaf 120s → orch 240s → parent 300s
B6 — can\_dispatch() mandatory before every batch (see Phase 3d)
```
\*\*Leaf Dynamic Split:\*\* a leaf that evaluates its task as too complex (3+ files with dependencies, estimate >120s) can spawn MAX 2 micro-workers. Micro-worker is dead-end (cannot spawn further). Context snapshot injected. If both fail → leaf implements inline (B4).
### 2b — Streaming Dispatch (wave-based)

Instead of one big `delegate_task(tasks=[...])`, dispatch in waves:
- Decompose goal into N tasks
- Dispatch BATCH 1 (tasks 1-25), prepare BATCH 2
- On first result → evaluate IMMEDIATELY → retry below-threshold without waiting
- Retries interleave naturally. Zero dead time between batches.
- **⚠️ Safety:** every batch MUST pass `can_dispatch()` (Phase 3d) before starting.

### 2c — Subagent Prompt Template (self-aware)

Every subagent knows it's part of a larger loop:

```
TASK: {description} | YOUR ID: {task_id} | THRESHOLD: {threshold}/10 | MAX ITERATIONS: 3
QUALITY CRITERIA: {custom_criteria}
SELF-AWARENESS: You are one of {total_tasks} parallel agents. Evaluated automatically. Below threshold = retry with feedback.
INSTRUCTIONS: (1) implement fully (no stubs/TODO), (2) self-verify, (3) fix if below threshold (max 3 tries), (4) return honest score + gaps.
PARTIAL SAVE: write partial results to .partial file every 120s. On timeout, main agent reads it.
RETURN FORMAT: ## RESULT - task_id - status: pass|fail|partial - quality_score: N/10 - gaps: [list] - files_created: [paths]
```
### 2d — Streaming Gather

```
while goal_not_achieved AND iteration < max:
  result arrives → parse status, score, gaps, files_created → validate files exist, no stubs
  if score >= threshold → mark complete | if score < threshold → IMMEDIATE RETRY (don't wait)
  update first_pass_rate, avg_quality
  if ALL accounted for AND all passed → 🎉 GOAL ACHIEVED
```

### 2e — Pre-Dispatch Validation

```
□ Each task has DIFFERENT files (no conflicts) | Load balanced (no task > 2× average)
□ Task count <= available subagents | Interface contracts documented (Phase 1d)
□ Assembly task planned for shared files (Phase 3g) | can_dispatch() passed (Phase 3d)
```
---
## Phase 3 — Streaming Quality Gate
### 3a — Security Shield AUTO (regex-based, ALL tiers)
\*\*Applied to ALL code-producing tasks, even Tier 1.\*\* If a check fails → immediate retry with specific feedback.
```
SECURITY AUTO CHECK (run after file validation, before quality gate):
1. ZERO HARDCODED SECRETS (CRITICAL — blocks task):
├─ Regex: \b(api\_key|password|secret|token|api\_secret)\s\*=\s\*['\"][^'\"]{8,}
│ WITHOUT os.getenv / env / process.env in next 3 lines
├─ Blocks: "API\_KEY = 'sk-abc123...'", "password = 'admin'"
├─ OK: "API\_KEY = os.getenv('API\_KEY')", "password = get\_secret()"
└─ If found → ❌ RETRY: "Move credential to environment variable"
2. SQL INJECTION RISK (HIGH — blocks task):
├─ Regex: (f['"]SELECT|f['"]INSERT|\.format\(.\*SELECT|\+ .\*SELECT|execute\(.\*\+)
├─ Blocks: f"SELECT \* FROM users WHERE id={user\_id}"
│ "SELECT \* FROM " + table\_name
├─ OK: cursor.execute("SELECT \* FROM users WHERE id=?", (user\_id,))
│ session.query(User).filter(User.id == user\_id) [ORM]
└─ If found → ❌ RETRY: "Use parameterized queries or ORM, never f-string SQL"
3. PLACEHOLDER SECRETS (warning — doesn't block):
   ├─ Regex: \b(API_KEY|TOKEN|SECRET)\s*=\s*(['"]\s*['"]|None|''|"")\s*#\s*TODO
   └─ If found → ⚠️ WARNING (may be intentional)

4. DEPRECATED API PATTERNS (HIGH — blocks task):
   ├─ Regex: \.__fields__\b|\.dict\(\)|\.json\(\)|pydantic\.v1|from typing import.*Type|@app\.route\([^)]+\)\s+\ndef
   ├─ Blocks: Pydantic v1 __fields__ access, bare .dict()/.json() calls, old typing imports
   ├─ EXCLUDES: files in /tests/, /test_*.py, /conftest.py (external test code uses hasattr(..., '__fields__') legitimately)
   ├─ OK: SQLAlchemy/SQLModel patterns, @app.route with HTTP methods, hasattr check in test files
   └─ If found → ❌ RETRY: "Use current version APIs — check for deprecation alternatives"
```
### 3a-quinques — Parallel Sandbox Racing

For critical tasks: 3-5 identical subagents in parallel, first to pass wins.

**When to activate:**
| Condition | Racing? |
|-----------|:-------:|
| First attempt (iteration 0) | ❌ No |
| Critical task (Tier 3+, hotfix) | ⚡ Auto |
| After 1 retry failed | ✅ 2 variants |
| After 2 retries failed | ✅ 5 variants |
| Quality-First Mode | ✅ Always 5 |

**Rules:** Different approach hints per variant. First to pass all gates wins. Max 5 variants. Never for shared files.
**⚠️ COST:** N variants = N× tokens. Use only for critical/hotfix where time > cost.

### 3b — Physical File Validation (MANDATORY for Tier 2-4)
**Not optional anymore.** Every code-producing task MUST pass this before being marked complete. Doc/config tasks → skip.
```
VALIDATE RESULT (mandatory for code tasks):
1. read_file(task.files_created[0]) — exists? → if not, ❌ fail immediate
2. grep -n "TODO\|pass\|stub" task.files_created — dead code? → ❌
3. python -c "from task.module import ..." — syntax ok? → ❌
4. wc -l task.files_created — file not empty? → ❌
5. FORMAT & ERROR HANDLING VALIDATION (for data/DB/API tasks):
   ├─ For SQL tasks: verify parameterized queries — grep for "?" or "%s" or ":param" after "execute("
   │   └─ If raw string interpolation found → ❌ RETRY: "Use parameterized queries"
   ├─ For API tasks: verify error handling — grep for "try:" OR "HTTPException" after external calls
   │   └─ If neither found → ❌ RETRY: "Add error handling (try/except or raise HTTPException)"
   ├─ For data analysis tasks: verify output format matches expected schema
   │   └─ Check: output type matches spec (dict, list, DataFrame, str)
   └─ For ALL tasks: grep for deprecated patterns from Phase 3a check 4
       └─ EXCLUDES: files in /tests/, /test_*.py, /conftest.py
       └─ If found → ❌ RETRY with specific deprecation feedback
```
If physical validation fails → **immediate retry with specific feedback** (no silent failure).
### 3c — Execution Reality Check (for standalone scripts and tests)
For \*\*standalone scripts, pure functions, or unit tests\*\*, run the code in sandbox:
```
EXECUTION CHECK (only for sandboxable tasks):
1. Run pytest test\_file.py or python script.py in sandbox
2. If stderr empty → ✅ pass
3. If stderr has errors:
├─ Use the EXACT error as retry feedback
├─ Max 3 fix attempts based on stderr
└─ If still failing → escalate to Phase 3j
DO NOT run if task requires:
├─ External DB/network connections
├─ Real filesystem (use tmpfile)
├─ Tokens/auth/API keys
└─ Listening server
```
### 3d — Context Window Protection (CRITICAL for Tier 3-4)

100 summaries = 200K tokens → context overflow → death spiral.

```
CONTEXT BUDGET RULES:
1. If N_subagents × 2000 > context_budget × 0.6 → REDUCE batch (2-3 waves)
2. Wave dispatch: batch > 20 → waves of 20, collect → process → free context
3. Summary compression: Tier 2 <500 tokens | Tier 3 <1000 | Tier 4 <2000
4. 2+ compression triggers → context saturated, reduce subagents
4. Compression death spiral prevention:
   ├─ If context compression triggers 2+ times in one session:
   │   └─ ⚠️ CONTEXT SATURATED — reduce subagents or summary size
   │   └─ Switch to smaller wave dispatch
   └─ Never ignore compression triggers — they signal overflow

5. HARD TIMEOUT GUARD (PREVENTS SILENT FAILURES):
   ├─ HARD CAP: 450s per task. On timeout → kill subagent, DO NOT leave at 0/100
   │   └─ Generate partial result: what WAS produced, what was missing. Score: 4/10 minimum.
   ├─ TIMEOUT ESCALATION: 1st → re-dispatch as 2 smaller | 2nd → inline | 3rd → Phase 3j-bis
   └─ TIMEOUT RATE TRACKING: >10% timeout → reduce batch 50% | >25% in 3 batches → downgrade Tier
```

**Cost:** 100 summaries saturate context → compression death spiral. Wave dispatch + summary compression prevent this.

### 3e — Adaptive Threshold Tuning (next batch only)

```
FPR < 60% after 25% of tasks → double granularity (split each in 2)
FPR > 90% after 25% of tasks → merge adjacent tasks
⚠️ NEVER change already-dispatched tasks — overlaps and conflicts.
```

### 3f — Actor-Critic Escalation (3+ retries only)

Not for every task. Analyzes failure pattern after 3+ retries: same error → context problem | different errors → execution problem | worsening → circular learning | stalemate → poorly specified.
Action: rewrite task, split, or escalate. Limit: 1 attempt per task.

### 3g — Git Commit+Push Policy (MANDATORY)

```
1. Task PASSES quality gate + files validated → git add + commit + push (exclusive files only)
2. SHARED files (router, __init__, config) → WAIT for assembly task post-batch
3. DO NOT commit in-flight task files (conflicts)
4. Commit format: conventional commits (feat/fix/test:)
5. Push fails → single retry, continue loop. Report "N commits not pushed" in final.
6. ASSEMBLY TASK: after ALL batch tasks verified → modify shared files, DRY check, commit + push
```
\*\*Why in the loop and not at the end:\*\* granular commits after every task = rollback possible for single task if a later task breaks it. Single final commit = all-or-nothing.
### 3h — Retry Intelligence

| Type | Score | Strategy |
|------|-------|----------|
| Superficial | 5-6 | Same task + feedback |
| Structural | 3-4 | Redefine + architectural hint |
| Critical | 0-2 | Rewrite, split into micro-tasks |
| Silent | N/A | Pivot inline |

### 3i — Convergence-Based Limits

```
if score improved ≥ 2 → continue (converging)
elif improved < 2 → change strategy (split, better hints)
elif WORSENED → stop, restart with smaller task
```

### 3j — Escalation Ladder

```
1. Self-verify → 2. Retry with feedback → 3. Change strategy → 4. ESCALATE TO USER → 5. User decides
```
**Rule:** never reach step 4 without 3 different strategies.

### 3j-bis — Graceful Degradation on Timeout

Problem: code_review/large refactors produce 0/100 on timeout — binary fail.

```
TIMEOUT GRACEFUL DEGRADATION (450s cap):
1. First timeout → re-dispatch as 2 smaller tasks, deadline "Return SOMETHING within 60s"
2. Second timeout → run yourself (inline), produce minimal viable version (stubs OK)
3. Third timeout → grep for patterns, return PARTIAL with explicit gaps
4. HARD RULE: Never 0/100 — always produce SOMETHING (5/100 > 0/100)
5. PRE-EMPTIVE SAVE: subagent writes .partial file every 120s → on timeout, read it for what was completed
```
### 3k — Global Re-Check Pass

Post-assembly: read ALL files for cross-module inconsistencies (signatures, naming, dead code, architecture).

**Activation triggers:**
| Condition | Re-Check? |
|-----------|:---------:|
| Quality-First Mode | ✅ Mandatory |
| Tier 4 (50+ files) | ✅ Yes |
| Tier 3 with 8+ files | ✅ Yes |
| 5+ cross-module deps | ✅ Yes |
| Tier 1-2 | ❌ Skip |
| < 8 files AND tier < 3 | ❌ Skip |
| Text-only tasks | ❌ Skip |

**Scans:** (1) signature consistency, (2) naming conventions, (3) dead code, (4) architectural layer violations.
**Resolution:** fail → create fix tasks, retry once. Still failing → include in final report.

---
## Phase 4 — Self-Learning Loop
### 4a — Pattern Capture (3-Level Persistence)

After every execution, save patterns at 3 levels:

| Level | Where | Size | When |
|-------|-------|------|------|
| 1. Memory Entry | Hermes memory store | Max 200 chars | Last batch of session |
| 2. Pattern Cache | `skill_dir/pattern_cache.json` | JSON, zero token cost | FPR > 70% |
| 3. Dedicated Skill | `skill_manage(action="create")` | Full SKILL.md | 3+ occurrences, FPR > 75% |

**Level 1 format:** `ES[goal_type|T{tier}] FPR={rate} dec={pattern} q={quality} iter={N} L: {lessons}`
**Level 2 consult:** at Phase 1 start, if goal_type matches cached pattern with FPR > 80% → use as template (saves ~2000 tokens).
**Level 3 trigger:** if same goal_type appears 3+ times with FPR > 75% → create skill.

### 4b — Adaptive Calibration
```python
def calibrate(history):
if len(history) < 3: return defaults()
avg = mean(h.first\_pass\_rate for h in history[-3:])
if avg < 0.6: return {"granularity": "fine", "threshold": threshold - 0.5}
if avg > 0.95: return {"granularity": "coarse", "subagents": subagents \* 0.7}
return {"granularity": "balanced"}
```
### 4c — Token-Efficient Recall (pre-loop sequence) — MANDATORY

**CRITICAL:** Recall is NOT optional. Skipping it is the #1 reason FPR degrades across sessions.

```
RECALL SEQUENCE (~1000 tokens):
1. Memory injection: ES[...] entries in context → match goal_type? → MUST use as template
2. Pattern cache: read_file(skill_dir/pattern_cache.json) → FPR > 70%? → MUST use as template
   ⚠️ CRITICAL: pattern_cache.json MUST be saved to SKILL DIRECTORY, not ~/.hermes/ (sessions are isolated)
3. Skill list: pattern-{goal_type} exists? → load with skill_view
4. Dynamic Knowledge: read local-patterns.md + dynamic-patterns.md → inject as extra_criteria
5. Calibration: 3+ history entries? → calibrate BEFORE decomposing
6. FPR enforcement: FPR < 60% → finer granularity | FPR > 90% → coarser | never decompose from zero
```

**Enforcement:** pattern found but ignored → -5 penalty on final report. Token savings: 60-75%.
### 4d — Self-Learning Feedback Loop (cross-session)

**Cycle:** RECALL (read cache + memory) → EXECUTE (calibrated params) → CAPTURE (Level 1+2) → CALIBRATE (update params). After 3+ sessions with FPR > 75% → create skill (Level 3).
**Measurable:** FPR MUST increase over 5 sessions. If not → re-evaluate lesson format.
### 4e — Self-Learning Guardrails (CRITICAL — 10 guardrails, non-optional)

| # | Guardrail | Rule |
|:--|:----------|:-----|
| 1 | **Memory Budget Cap** | Max 10 ES[...] entries. If >8, replace oldest/lowest FPR. Never add — replace. |
| 2 | **Lesson Validation** | Only save evidence-based lessons (failed test → fix). Skip anecdotes, opinions, self-referential claims. Anti-circularity test: "If this lesson were wrong, how would I know?" |
| 3 | **Skill Mutation Protection** | Pitfalls/references/examples: auto-patch allowed. Philosophy/Tier/Quality/Guardrails/Phases: human confirmation REQUIRED. Max 1 patch/session. |
| 4 | **Skill Proliferation Cap** | Max 5 pattern-* skills total. Consolidate if >70% similar. Max 1 created/session. Archive if unused 30 days. |
| 5 | **Pattern Cache Cleanup** | Cleanup every 10 batches: keep ≤20 entries. If >50: EMERGENCY keep only 10 recent with FPR>70%. Delete goal_types with 3+ entries FPR<60%. |
| 6 | **Project Isolation** | Architecture/structure lessons = PROJECT-LOCAL (./.hermes/local-patterns.md). Pure technology (API/framework) = GLOBAL (~/.hermes/references/dynamic-patterns.md). When in doubt → LOCAL. |
| 7 | **Human Checkpoint** | skill_manage create/delete/edit → user confirmation. Patch pitfalls/references → notify after. Dynamic knowledge files ([Auto]) — autonomous. |
| 8 | **Session Memory Flush Cap** | Max 3 memory entries/session, 1 skill patch/session, 1 pattern_cache update (last batch only). Overflow → save top-N by impact. |
| 9 | **Drift Detection** | Every 5 sessions of same goal_type: compare FPR. If dropped >10% → stop saving, alert user, propose reset. |
| 10 | **Transparency Log** | Final report MUST list: entries saved/replaced, cache updated, skills patched/created, lessons validated/rejected, guardrails activated. |

**Self-learning is autonomous in DETECT (what to learn) but collaborative in ACT (structural changes need human consent).**
### 4f — Dynamic Knowledge Expansion (post 3+ retry) — Local/Global Split

**Trigger:** 3+ retries to pass quality gate → knowledge worth capturing.
```
1. Extract: What failed? Why? What solution worked?
2. Classify SCOPE:
   ├─ GLOBAL (pure tech: APIs, frameworks, languages) → ~/.hermes/references/dynamic-patterns.md
   └─ LOCAL (project architecture, conventions, wrappers) → ./.hermes/local-patterns.md
3. Auto-load: LOCAL always, GLOBAL filtered by technologies in goal
4. DEFAULT: when in doubt → LOCAL (harmless noise vs damaging context pollution)
```
### 4g — Lesson Hierarchy

| Priority | Type | Rule |
|:--------:|:-----|:-----|
| P0 | Structural | Always save (changes future decomposition) |
| P1 | Task-specific | Save if recurring (add extra quality criteria) |
| P2 | Context-specific | Save if project recurring (pitfall to check) |
| P3 | One-off | **NEVER save** — log in STATE only |

**Rule:** less but better. Max 2-3 lessons per batch.
### 4h — Skill Self-Improvement
- If a decomposition pattern succeeds 3+ times → save as reusable pattern
- If a pitfall is discovered → add to pitfalls section (general, not project-specific)
- Each self-improvement action bumps the skill version (following the v0.7.x scheme):
- Patch fix (v0.7.1) → new pitfall or minor calibration
- Minor improvement (v0.8.0) → new pattern or phase
- Major rewrite (v1.0.0) → breakthrough architecture change
---
## Phase 5 — Final Report

```
## ✅ [Goal]
### Loop Efficiency: subagents N/M | FPR XX% | quality X.Y/10 | duration X min
### Self-Learning: pattern saved, lessons, calibration, guardrails activated
### Quality: ✅ Passed X | ⚠️ Gaps Y | ❌ Escalated Z
### Self-Feedback: XX/100 | notes: [strengths + improvements]
```
---
## Phase 6 — Quality Matrix

**Scoring Rubric (0-10):**
| Score | Label | Action |
|-------|-------|--------|
| 10-9 | Flawless/Excellent | Accept |
| 8-7 | Good/Solid | Accept |
| 6-5 | Adequate/Weak | Retry with feedback |
| 4-3 | Poor/Bad | Redefine + split |
| 2-0 | Critical/Broken/Silent | Rewrite or pivot inline |

**Rules:** score = completeness + bonus (edge cases, tests) − penalty (stubs, conflicts). Ambiguous → lower bound. Silent (0) → immediate pivot.

**Per Task:** no stubs/TODO, edge cases, error handling, conventions, security shield, physical validation.
**Per Batch:** all delivered, files exist, no conflicts, no orphans, context OK, git checkpoint.
**Per System:** FPR saved, quality documented, pattern captured, calibration updated, goal achieved (not timeout).
---
## Phase 7 — Self-Execution Infrastructure

Supporting files in the skill directory: `scripts/init-state.sh` (bootloader), `references/pattern-store.sql` (SQLite schema), `scripts/install.sh` (installer), `scripts/session_manager.py` (state tracking), `scripts/e2e_test.py` (176 tests).

| MCP Server | Phase | Usage |
|-----------|-------|-------|
| **sqlite** | Phase 4, 7a | Pattern persistence, calibration |
| **graphify** | Phase 0b | Codebase context, dependency analysis |
| **sequential-thinking** | Phase 1, 3f | Complex reasoning, Actor-Critic |
| **github** | Phase 7e | GitHub sync, code review |

Cron: `cronjob schedule: "0 6 * * *"` for daily health scan, weekly refactor, on-demand deploy.
GitHub: `git add -A && git commit -m "v0.x" && git push origin main`. MIT license.
```bash
git add -A
git commit -m "v0.6 — description of improvement"
git push origin main
```
The skill is public (MIT license). Every meaningful improvement bumps the version.
---
## Phase 10 — Skill Ecosystem Integration

Complementary skills loaded during the loop:

| Phase | Skill | Why |
|-------|-------|-----|
| 1 (Decompose) | `test-driven-development` | RED→GREEN→REFACTOR for code tasks |
| 3 (Validation) | `verification-strategies` | When no test suite: curl, type checks, import checks |
| 3 (post-batch) | `requesting-code-review` | Security scan, quality gates, auto-fix |
| 3j (Escalation 1) | `systematic-debugging` | Root-cause analysis after 3 retries |
| 3j (Escalation 2) | `post-mortem` | 5 Whys + regression test + memory feed |
| Post-batch (T3+) | `deploy-release` | Version bump, changelog, deploy, health check |

---
## Phase 11 — Long Session Management

For sessions 2h+ with 30+ turns. Problem: quality degrades as context saturates.

**3 Mechanisms:**
1. **Session State File** — `SessionManager` tracks turns/decisions to `~/.hermes/sessions/` JSON. Context summary ~200 tokens.
2. **Automatic Checkpoint** — every 8 turns or 10 min: compress past turns, keep last 3 detailed.
3. **Quality Trend Monitor** — detect degradation in last 5 evaluations → alert + simplify next tasks.

**Interrupt Recovery:** `sm = SessionManager(id, goal); recovery = sm.recover()` restores state from disk.
**Context Summary** (when >60% saturated): `=== SESSION STATE: {id} === Goal: {goal} Turns: {N} Quality: {X}/10 Files: {list} Decisions: {list}`
- [{turn}] {decision}
Last checkpoint: turn {turn}
⚠️ Quality is degrading — simplify next tasks.
```
---
## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init-state.sh` | Bootloader: auto-detect tier, --clarify, --quality-first, --plan-file, --structural-scan |
| `scripts/install.sh` | Auto-installer |
| `scripts/e2e_test.py` | 176 checks across ALL phases, tiers 1-4 |
| `scripts/session_manager.py` | Session state tracking, checkpoint, quality trend, interrupt recovery |
| `scripts/pattern_cache.json` | Local pattern cache (created automatically, persists across sessions) |

Run validation: `python scripts/e2e_test.py`

---
## Pitfalls (condensed — 22 rules)

| # | Pitfall | Fix |
|:--|:--------|:----|
| 1 | Loop not autonomous (plan-plan-act) | assess → act → repeat |
| 2 | Streaming gather forgotten | Retry on first below-threshold result |
| 3 | Non-adaptive decomposition | Scale with available subagent slots |
| 4 | Scale patterns unused | Use multi-variant for 100 subagents |
| 5 | Self-learning skipped | Save patterns, calibrate, improve |
| 6 | Quality threshold ignored | Calibrate, don't ignore |
| 7 | Escalation hidden | Follow escalation ladder |
| 8 | Same decomposition for all goals | Match scale pattern to goal type |
| 9 | Idle during dispatch | Prepare retry templates while waiting |
| 10 | No physical file verification | Verify with read_file/stat |
| 11 | State not updated per result | Update after EVERY result |
| 12 | Overfitting self-learning | Need 3+ confirmations |
| 13 | Tier 4 for Tier 1 tasks | Fast-path exists for a reason |
| 14 | Context window overflow | Wave dispatch, summary compression |
| 15 | Security in subagent output | Always run Phase 3a Security Shield |
| 16 | No guardrails on self-learning | Phase 4e is NON-OPTIONAL |
| 17 | Signature mismatch (parallel) | Shared Interface Contracts (Phase 1d) |
| 18 | Clarification skipped (Tier 3+) | Always ask 5-6 questions first |
| 19 | Plan skipped (5+ files) | Write plan before dispatch |
| 20 | Sandbox Racing on shared files | Racing is for isolated bugfixes only |
| 21 | Skipping Phase 0.6 exploration | Tier 3+ defaults to 1st approach. Always run 3 scouts or load cached winner. |
| 22 | Ignoring auto-update notification | "v{NEW} available" means real improvements. Run git pull + /reload-skills. |
---
## Version History

```
v0.11.1 — Auto-Update Bootstrap. Skill now self-maintaining: git-based version
         check at every activation (compare LOCAL vs REMOTE, notify user if
         newer available). Install.sh updated: auto-inits git repo in skill_dir
         with origin→GitHub remote. git pull + /reload-skills = instant update.
         Never auto-updates without consent (Guardrail #7). New pitfall #22.
         Bootstrap section added after Required Config.

v0.11.0 — Solution-Space Exploration. Phase 0.6 adds automatic multi-strategy
         exploration for ALL Tier 3+ tasks. 3 strategy scouts (biased: simplicity,
         scalability, speed) → trade-off matrix (5 axes, weighted scoring) →
         winner selection with anti-bias check → synthesis if top 2 within 15% →
         approach-type pattern capture for skip-on-repeat. Core Loop + Quick
         Start updated with explore() step. New pitfall #21. 3 new tags.
         906→1025+ lines.

v0.9.1 — Skill problems fix release + 4-Band Filter unification. 7 fixes, 1458→965 lines (-34%).

         FIX #1 (Self-learning persistence): pattern_cache.json now saved to
         SKILL DIRECTORY (not ~/.hermes/). Each hermes chat session is isolated —
         only files in the skill directory persist across sessions. Phase 4c updated.

         FIX #2 (Pydantic __fields__): Phase 3a check 4 now EXCLUDES files in
         /tests/, /test_*.py, /conftest.py (external test code uses hasattr(...,
         '__fields__') legitimately).

         FIX #3 (FastAPI HTTPException): Phase 1c point 4 now recognizes
         `raise HTTPException(status_code=...)` as valid error handling (FastAPI idiom).

         FIX #4 (4-Band Filter thresholds): Tier 2 now explicitly includes
         "single CRUD endpoint". Tier 3 requires "auth+CRUD+services".
         "Single endpoint + model + tests = Tier 2, NOT Tier 3".

         FIX #5 (Global Re-Check conditional): threshold raised from <5 files to
         <8 files AND tier < 3. Skip for Tier 1-2 regardless.

         FIX #6 (Graceful degradation): Phase 3j-bis now has 450s cap (was 300s/180s).
         5-level degradation: re-dispatch → inline → partial → .partial file read.
         "Never 0/100 — always produce SOMETHING".

         FIX #7 (Pre-emptive save): subagent MUST write partial results to .partial
         file every 120s. On timeout → main agent reads .partial for what was completed.
         Score partial result: completed_files × (max_score / total_files).

         COMPRESSION: 1458→906 lines (-38%). Sections compressed:
         - Phase 0a (State): 95→42 lines
         - Phase 0.5a/0.5b/0.5c: 68→30 lines
         - Phase 1b (Scale Patterns): 15→7 lines
         - Phase 1d (Interface Contracts): 15→8 lines
         - Phase 2b (Streaming Dispatch): 15→7 lines
         - Phase 2c (Subagent Prompt): 25→6 lines
         - Phase 2d (Streaming Gather): 10→5 lines
         - Phase 2e (Pre-Dispatch): 10→3 lines
         - Phase 3a-quinques (Sandbox Racing): 40→15 lines
         - Phase 3c (Execution Check): 15→8 lines
         - Phase 3d (Context Protection): 20→10 lines
         - Phase 3e (Adaptive Threshold): 12→5 lines
         - Phase 3f (Actor-Critic): 15→3 lines
         - Phase 3g (Git Policy): 20→8 lines
         - Phase 3h/3i/3j: 25→12 lines
         - Phase 3j-bis (Graceful Degradation): 25→8 lines
         - Phase 3k (Global Re-Check): 40→15 lines
         - Phase 4a (Pattern Capture): 35→12 lines
         - Phase 4c (Recall): 35→12 lines
         - Phase 4d (Feedback Loop): 20→3 lines
         - Phase 5 (Final Report): 20→5 lines
         - Phase 6 (Quality Matrix): 40→15 lines
         - Phase 7 (Infrastructure): 70→15 lines
         - Phase 10 (Ecosystem): 30→12 lines
         - Phase 11 (Long Session): 70→12 lines
         - Scripts: 17→8 lines
         - Pitfalls: 80→25 lines

v0.9.0 — Evidence-based release. NESSUN claim senza artefatto eseguibile e versionato.

         FASE 1 ✅ Accesso Elysium-Bench confermato (lettura+scrittura).

         FASE 2 ✅ Ceiling effect CONFERMATO:
         - 3 soluzioni rotte (syntax error, wrong return, minimal stub)
           → correctness=0.0 (tests falliscono)
         - 1 soluzione corretta (CRUD completo)
           → correctness=40.0 (tests passano, pytest returncode=0)
         - Ipotesi confermata: il scorer FUNZIONA, le soluzioni benchmark
           passano tutti i test → correctness è sempre al massimo.
         - Artefatti: risultati/correctness_falsification_test/

         FASE 3 ✅ DataScoringEngine fix VERIFICATO 5/5:
         - 5 coppie (buona/scadente): SQL sales, Pandas cleaning,
           SQL JOIN, Pandas merge, SQL subquery
         - GOOD: 46.7-91.7 | BAD: 40.0 (costante)
         - completeness/efficiency/robustness/clarity differenziano
         - correctness resta 40.0 per entrambi (validate.py exit 0)
         - Artefatti: risultati/dataengine_verification/

         FASE 4 ⚠️ BLOCCATA: ri-benchmark medium con 6 loop non eseguito.
         Motivo: richiede esecuzione Hermes+skill completa (30-60 min)
         non fattibile in questa sessione. Prerequisito: Fase 2+3 ✅.
         Self-learning Δ resta "non verificato".

         FASE 5 ✅ Testo pubblico aggiornato SOLO con numeri tracciabili:
         - description: riferimenti a test specifici
         - transparency note: risultati verificati per fase
         - Philosophy caveat: self-learning non ri-benchmarkato
         - Version History: stato fase-per-fase esplicito
         - README.md: caveat visibile sotto badge

         KNOWN UNFIXED:
         - correctness=40.0 per data tasks (validate.py exit 0)
         - Self-learning Δ non verificato (richiede 6+ loop)
         - BENCHMARK_RESULTS.md vecchi claim non aggiornati
           (caveat già presente da v0.8.2, lasciato invariato)
v0.8.3 — Transparency release: aligned frontmatter to audit reality (description
         softened from "Self-Improving" to "self-learning mechanisms, efficacy
         not yet independently verified"). Added transparency note at top of
         SKILL.md and README.md. Added caveat to Philosophy "I improve myself"
         claim. README self-learning bullet now carries audit asterisk. README
         badge updated to v0.8.3. Version history reference to rebrand explained.
         
         SCORER FIX (in Elysium-Bench repo, not here):
         DataScoringEngine._rubric_check() was returning static max_score * 0.3
         when no rubric.yaml existed → invariant 58/100. Fixed with content-aware
         heuristics (SQL keywords, Pandas usage, error handling, comments).
         Test: good solution=50.0 vs bad solution=4.5 (was both 58.0).
         CodeScoringEngine correctness=40.0 is NOT a bug — it's a ceiling effect
         (all tests pass → max_score). Varying test difficulty would fix this.
         
         TODO (claims not yet updated with audit reference):
         - BENCHMARK_RESULTS.md "100% test pass" claim needs asterisk
         - README "What's New" sections reference old version numbers
         - SKILL.md Phase 4d "FPR should improve" needs caveat
         - SKILL.md Phase 5 report template "Self-Learning" section needs caveat
         - New benchmark run with fixed DataScoringEngine not yet executed
v0.8.2 — Accountability release: auditing mission. No feature changes. Added
         AUDIT_SCORING_ENGINE.md documenting invariant correctness=40.0 across all
         benchmarks (54/54 non-timeout tasks). Fixed hygiene: removed hardcoded
         user path (leob3) from SETUP.md, aligned README badge to v0.8.2. Added
         explicit cost warning to Sandbox Racing (Phase 3a-quinques). Version
         History now documents the v5.1.0→v0.6.0 rebrand.
         Known issue tracked: DataScoringEngine returns invariant scores for
         data tasks — NOT fixable in this skill (external benchmark code).
v0.8.1 — Timeout calibrated to 450s (optimal sweet spot: code_review 265s + 185s
         buffer, eliminates v0.8.0 Re-Test regression on bug_fixing/algorithm).
         Phase 3d + 3j-bis aligned to 450s.
v0.8.0 — Performance & accuracy improvements: timeout raised to 300s (aligns
         with B5 orchestrator depth-3), 4-Band Filter word-boundary matching
         (prevents false Tier 3 from "api" substring), Clean Code filtered to
         code-only tasks + FastAPI HTTPException recognition, Tier 1 Fast-Path
         expanded (≤2 files + no deps = guaranteed Tier 1), Global Re-Check
         conditioned (skip if <5 files or tier<3), guardrails compressed from
         135→20 lines (compact table format), Phase 4f/4g compressed.
         1497→1358 lines (-9%).
v0.7.2 — Benchmark-driven fixes: recall enforcement (Phase 4c — matched patterns
         MUST be used, calibration mandatory before decompose, FPR enforcement),
         timeout guard (Phase 3d point 5 — hard cap 180s, timeout escalation
         ladder, never leave 0/100, partial result on timeout, batch reduction),
         deprecation check (Phase 3a check 4 — Pydantic v1, old typing imports, bare .dict()/.json()),
         error handling standards (Phase 1c point 4 — mandatory try/except on
         external calls, API error codes, bare except ban),
         format validation (Phase 3b point 5 — SQL parameterized queries, API
         error handling grep, data format schema check),
         graceful degradation on timeout (Phase 3j-bis — partial result instead
         of 0/100, 3-level degradation ladder).
         1360→1430 lines.
v0.7.1 — Scripts table update for e2e_test.py + validation run instructions.
New pitfall: keyword substring over-matching in tier/band detection
("api" in "/api/users/" → false tier 3, "system" → false tier 4).
v0.7.0 — NEW FEATURES: Phase 0.5a (Clarification Interview — 6 pre-flight
write decomposition plan to .hermes/plans/ before dispatch, preventing file
conflicts), Phase 0.5c (Structural Alignment — auto-scan existing project
conventions before creating files), Phase 3a-quinques (Parallel Sandbox Racing —
3-5 simultaneous variants for critical bugfixes, first to pass wins), Phase 3k
(Global Re-Check Pass — post-assembly integrity scan for cross-module signature
mismatches, naming drift, dead code, architecture violations), Quality-First Mode
Override (threshold 9/10, 9 iterations, global re-check on demand), Hard Trigger
Activation (bypass 4-Band Filter with "attiva elysium"/"massima qualità"
keywords), User Preferences Template (YAML-configurable language, auto-commit,
auto-push, test_command), Config Prerequisites section (mandatory hermes config
settings documented in SKILL.md), E2E Test Script (scripts/e2e_test.py — 35+
automated tests, 4 scenarios), Enhanced Session Manager (scripts/session_manager.py
— checkpoint, quality trend, interrupt recovery). 920→1360 lines.
v0.6.0 — Major upgrade: Security Shield AUTO, Context Window Protection,
Physical File Validation (3b), Execution Reality Check (3c),
Adaptive Threshold Tuning (3e), Actor-Critic Trigger (3f),
Git Commit+Push Policy (3g), Shared Interface Contracts (1d),
Clean Code Standards (1c), Codebase Familiarity Override (0a),
4-Band Filter, Precedence Rule, Subagent Prompt Template (2c),
Streaming Dispatch (2b), 3-Level Pattern Capture (4a),
Token-Efficient Recall (4c), Self-Learning Feedback Loop (4d),
10 Self-Learning Guardrails (4e), Dynamic Knowledge Expansion (4f),
Lesson Hierarchy (4g), Skill Ecosystem Integration (Phase 10),
Long Session Management (Phase 11), B1-B6 Anti-Bottleneck (2a).
480→920 lines.
v5.1.0 — Tier definitions, quality scoring rubric, Phase 7 Self-Execution
         Infrastructure (bootloader, SQLite pattern persistence, MCP integration guide,
         cron integration, GitHub sync). Added 6 new pitfalls. 391→480 lines.
         
         ▲ VERSION RESET: After v5.1.0, the project was rebranded from
         "agentic-auto-pilot" to "Elysium Swarmloop" and the versioning was reset
         to start from v0.1.0 for the public release. v5.1.0 and v0.6.0 are
         functionally consecutive — the jump is cosmetic, not a regression.
v5.0.0 — Elysium Swarmloop: rebranded from agentic-auto-pilot,
cleaned project-specific pitfalls, added depth-2 orchestration,
self-improvement guardrails, version bump discipline.
v4.0.0 — Autonomous loop engine, streaming gather, self-learning
v3.0.0 — Scatter-gather + quality threshold loop
v2.0.0 — Multi-agent parallel execution
v1.0.0 — Original guided workflow
```