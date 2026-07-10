---
name: elysium-swarmloop
description: "The Self-Improving Multi-Agent Orchestration Engine. Always-on autonomous agentic loop: prompt enhancement → deep research → massive scatter-gather (up to 100 subagents) → streaming quality gate (immediate retry on arrival) → self-learning iteration → loop until goal achieved with zero human intervention. Auto-activates on EVERY prompt."
version: 0.6.0
author: Boschi404 + ffazecaldy
testing-agent: Hermes Agent
tags: [agentic, auto, workflow, multi-agent, quality, research, iteration, scatter-gather, streaming-gather, self-learning, autonomous-loop, meta-scaling, orchestrator-depth2, self-improving, swarmloop, guardrails, security-shield, context-protection, contracts]
---

# Elysium Swarmloop
The Self-Improving Multi-Agent Orchestration Engine
*Towards Agentic Utopia.*

## Philosophy

**I don't follow a workflow. I am the loop. And I improve myself.**

Elysium Swarmloop is a self-improving autonomous orchestration engine that:

1. **Decides what to do next** — state machine, not recipe
2. **Executes at any scale** — 1 to 100 subagents per batch
3. **Orchestrates hierarchically** — depth-2: orchestrators spawn workers (depth-3 with B1-B6 rules for complex tasks)
4. **Evaluates and retries instantly** — streaming gather, no batching delay
5. **Learns and evolves** — captures patterns, calibrates, bumps version on improvement
6. **Validates at every layer** — security, file integrity, execution, context budget
7. **Protects itself** — 10 guardrails prevent self-learning contamination

**Guardrails for self-modification:**
- Every edit to this skill must **improve the autonomous workflow**, not add project-specific trivia
- No project error messages, framework-specific bugs, or dependency issues
- Each modification increments the PATCH version (v5.x), meaningful improvements bump MINOR (v5.x), breakthrough rewrites bump MAJOR (v6.0.0)
- When version bumps, the skill's own `# Changelog` section at the bottom gets a new entry

---

### ⚖️ Precedence Rule — Policy Conflict Resolution

When two sections describe alternative policies for the same moment in the flow, **the most restrictive wins** (safety > autonomy). Order of precedence:

1. ⚖️ **Precedence Rule** (this section) — always active
2. 🛡️ **Guardrails (Phase 4e)** — protect the system from itself
3. 🪜 **Escalation Ladder (Phase 3j)** — user decides on below-threshold gaps
4. 🧠 **Context Protection (Phase 3d)** — prevents overflow/saturation
5. 🎯 **4-Band Filter** — pre-check before loading skill
6. ✨ **Quality Gate (Phase 3)** — evaluates and retries
7. 📡 **Scatter (Phase 2)** — parallel dispatch

**Example:** if Quality Gate says "accept task below threshold" but Escalation Ladder says "escalate to user" → Escalation wins. If Phase 2 says "dispatch 50 streaming" but Context Protection says "max 20-25 in-flight" → Context Protection wins.

---

### 🎯 4-Band Filter — First Checkpoint (BEFORE everything)

**BEFORE loading the rest of the skill**, categorize the request into 4 bands. This determines HOW MUCH of the skill to activate.

| Band | Examples | Tier | Load skill? | Subagents | Loop? |
|------|----------|------|-------------|-----------|-------|
| **Low** | typo, fix bug, rename, change color, single command | 1 | ❌ No (saves 8K tokens) | 0 | No, direct |
| **Medium** | add endpoint, create function, test, refactor | 2 | ✅ Yes | 1-5 | 1 iteration |
| **High** | system, auth module, full API, multi-file feature | 3 | ✅ Yes | 5-30 | ∞ converge |
| **Extreme** | full-stack, e-commerce, MVP from zero, 50+ files | 4 | ✅ Yes | 30-100 | ∞ + orchestrator |

**Token saving rule:**
```
IF band == "low":
  └─ DON'T load SKILL.md (8K tokens saved)
  └─ Execute directly: read, edit, commit, push
  └─ No loop, no subagents, no plan

IF band == "medium":
  └─ Load SKILL.md, fast path: decompose → dispatch 1-5 → gather → done
  └─ Max 1 retry, no self-learning

IF band == "high" or "extreme":
  └─ Load full SKILL.md
  └─ Full loop with all phases
  └─ Self-learning active
```

**When in doubt, prefer the HIGHER band.** It's better to load the skill for a medium task and discover it was low, than to skip it for a high task.

---

## The Core Loop

```
while goal_not_achieved:
    state = assess(goal, done, gaps)
    if state.is_done: break
    decide()        # what to do next based on state
    decompose()     # break remaining work into tasks
    scatter()       # dispatch all in parallel
    stream()        # process each result as it arrives
                    # immediate retry on failures
    learn()         # save patterns, calibrate, improve
```

---

## 🚀 Quick Start

```
GOAL: "Crea sistema di prenotazione ristorante"

1. STATE INIT → tier 3, 50 subagenti, soglia 7/10
2. DECOMPOSE → 40 task atomici su 40 file diversi
3. SCATTER  → dispatch 40 subagenti in parallelo
4. STREAM   → processa streaming: 42 pass, 8 fail → retry immediati
5. CONVERGE → 3 iterazioni, 100% pass
6. LEARN    → salva pattern "decomposizione per_file per CRUD"
7. REPORT   → first-pass 84%, qualità 8.6/10, 5 minuti
```

---

## Phase 0 — Autonomous Loop Engine (ALWAYS ACTIVE)

### 0a — State

```python
STATE = {
    "goal": "prompt_enhanced",
    "tier": auto_detect(),
    "quality_threshold": tier_to_threshold(tier),
    "subagents_available": 100,
    "subagents_used": 0,
    "tasks_completed": [],
    "tasks_failed": [],
    "tasks_in_flight": [],
    "iteration": 0,
    "max_iterations": auto_calc(tier),
    "first_pass_rate": None,
    "avg_quality_score": None,
    "self_lessons": [],
    "codebase_familiarity": "unknown",  # NEW: track familiarity
    "start_time": now(),
}
```

#### Tier Auto-Detection

The tier is determined automatically when the loop activates:

| Tier | Subagents | Threshold | Fast-Path? | When |
|------|-----------|-----------|------------|------|
| **1 — Quick Hit** | 1-3 | 6/10 | ✅ Yes | Single edit, config change, simple command, one-liner |
| **2 — Standard** | 5-15 | 7/10 | ❌ | Feature add, bugfix, small refactor, single module |
| **3 — Complex** | 15-50 | 7/10 | ❌ | Multi-file feature, API endpoint, research task, medium project |
| **4 — Epic** | 50-100 | 8/10 | ❌ | Greenfield project, system redesign, cross-cutting integration |

**Tier 1 Fast-Path**: If the goal is a single atomic action (one command, one edit, one lookup), skip the loop entirely. Execute directly, return result. No state init, no self-learning.

**Tier detection heuristic:**
```
TIER 1: atomic action (1 file, 1 command, 1 question)
TIER 2: 1-3 files, familiar domain, < 1h estimated
TIER 3: 3-10 files, multiple domains, research needed
TIER 4: 10+ files, greenfield, cross-system, > 4h estimated
```

When in doubt, default to Tier 2 and let the assess phase escalate.

#### 🧠 Codebase Familiarity Override

The Tier system assumes **unknown** codebase. If you **already know the project** (explored in previous sessions, read key files), apply this override:

| Familiarity | Subagent Adjustment |
|-------------|-------------------|
| Never seen (first session) | Standard tier table |
| Explored in previous session | -50% subagents |
| Know by memory (read 5+ files) | -80% subagents (or 0) |
| Wrote the module yourself | 0 subagents, direct execution |

**Rule of thumb:** if you've already read the 5 main project files, you're Medium Familiarity. If you've written files in that project, you're High Familiarity. Reduce subagents proportionally. Dispatch overhead is not worth it on codebases you already know.

**The cost of 100 parallel subagents is 100× the cost of a single API turn.** Wasting them on simple tasks burns tokens and money. Use the minimum necessary.

#### State Initialization

The bootloader at `scripts/init-state.sh` automates STATE creation. Run it at loop start:

```bash
# From the skill directory:
bash scripts/init-state.sh "Your goal here"
```

Outputs a JSON STATE object ready for the loop.

### 0b — Assess

```
ASSESS:
1. Completed? (tasks_completed)
2. Failed? (tasks_failed + gaps)
3. In flight? (tasks_in_flight)
4. Goal reachable? (gaps vs remaining resources)
5. Adjust strategy? (first_pass_rate < 60% → finer granularity)
6. Past patterns for this task type? (query SQLite + memory)
7. Tier still correct? (goal complexity may change mid-loop)
```

### 0c — Decide

```
if in_flight:       → stream (wait for results)
elif failed & iter < max: → retry with enriched feedback
elif failed & iter >= max: → escalate to user
elif not started:   → decompose + dispatch
elif done & quality OK:  → COMPLETE → report + self-learn
elif done & quality LOW: → quality improvement loop
```

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
    if iteration == 0: return fine_grained(goal, count=available * 0.8)
    else:              return fine_grained(gaps, count=len(gaps) * 3)
```

### 1b — Scale Patterns

| Pattern | Subagents | When |
|---------|-----------|------|
| **Micro-Task Cascade** | 50-100 | Big project, one file per task |
| **Multi-Variant + Selection** | 30-50 | Critical component, 5 approaches, pick best |
| **Research → Implement → Test** | 50-100 | Need research before implementation |
| **Full System Build** | 80-100 | Greenfield full-stack MVP |
| **Data Pipeline** | 50-100 | Multi-source ETL, transform, merge, report |

**Data Pipeline Pattern (for data-heavy projects):**
```
Task 1-20:  Fetch data from 20 different sources
Task 21-40: Transform/normalize each source
Task 41-60: Analyze/metrics on each dataset
Task 61-80: Merge and correlate
Task 81-90: Generate reports/visualizations
Task 91-100: Review and quality check
```

### 1c — Clean Code Standards (by Tier)

**Do NOT apply to Tier 1** (quick fixes). For Tier 2-4, these are **mandatory** in subagent quality criteria:

```
CLEAN CODE STANDARDS (injected into quality criteria):

1. TYPE HINTS & DOCSTRINGS (Tier 2-4):
   ├─ Every function must have explicit type hints (params + return)
   ├─ Every public function must have a concise docstring
   │   └─ Format: [What it does]. Input: [params]. Output: [return]. Raises: [exceptions].
   └─ Validation phase checks type hint presence

2. SINGLE RESPONSIBILITY (Tier 3-4, via Actor-Critic):
   ├─ One function/class does ONE thing
   ├─ If an API route does DB query + business logic + email → ❌ FAILED
   ├─ Applied only after 3+ retries (not for every task — expensive)
   └─ Verified by Actor-Critic, not automatic regex

3. DRY — DON'T REPEAT YOURSELF (Tier 3-4, via Assembly Task):
   ├─ If two subagents produce duplicate code, the Assembly Task extracts
   │   it into a shared module (utils/ or config/)
   ├─ Applied POST-BATCH, not during individual dispatch
   └─ Verified by Assembly Task (Phase 3g point 6)
```

### 1d — Shared Interface Contracts (pre-dispatch)

Before dispatching subagents that produce calling/called modules (e.g. router.py → client.py), document the **complete function signatures** in the context of EVERY subagent involved.

**Rule:** if subagent A must call a function from subagent B, the exact signature (name, params, types, sync or async, return values) goes in BOTH contexts — not just the implementer.

**Example context block:**
```
--- INTERFACE CONTRACT ---
Called module: app/client.py (implemented by subagent B)

build_prompt(location: GeoResult, target_date: date, sources: list[str]) -> str
  NOTE: SYNCHRONOUS — caller uses `prompt = build_prompt(...)`

call_api(prompt: str, max_retries: int = 3) -> ApiResult
  NOTE: ASYNCHRONOUS — caller uses `result = await call_api(...)`

Calling module: app/router.py (implemented by subagent A)
  from client import call_api, build_prompt
  prompt = build_prompt(location=loc, target_date=d, sources=s)
  result = await call_api(prompt)
--- END CONTRACT ---
```

**Why critical:** parallel subagents implementing communicating interfaces without shared contracts produce mismatches — one uses `await build_prompt(...)`, the other defines `def build_prompt(...)`. The contract eliminates 90% of these integration bugs.

**⚠️ Dynamic dispatch limitation:** if Batch 1 has already started, Batch 2 MUST adapt to signatures already written by Batch 1 (read the produced file), not the other way around.

### 1e — Dynamic Quality Criteria

```python
criteria = {"completeness", "correctness", "edge_cases"}
if task_type == "api":    criteria += {"status_codes", "validation", "tests"}
if task_type == "model":  criteria += {"constraints", "repr", "migration"}
if task_type == "ui":     criteria += {"responsive", "states", "anti-slop"}
```

---

## Phase 2 — Hierarchical Scatter (Depth-2/3 Orchestration)

### 2a — Two-Level Hierarchy (+ B1-B6 Anti-Bottleneck)

With `max_spawn_depth: 2`, subagents can be orchestrators that spawn their own workers:

```
MAIN AGENT
  └── delegate_task(role="orchestrator", goal="Analizza e fixa modulo X")
       ├── worker "trova bug"         (leaf, default)
       ├── worker "trova vulnerabilità" (leaf)
       └── worker "propone fix"       (leaf)
```

**Rules:**
- `role="orchestrator"` → subagent can use `delegate_task(tasks=[...])` with leaf workers
- `role="leaf"` (default) → cannot delegate further
- Orchestrator collects worker results, synthesizes, returns summary
- Workers are always leaves at depth 2

**For Tier 4 (Epic, 50+ files) — Depth-3 with B1-B6 Anti-Bottleneck Rules:**

For very complex tasks, use 3-level hierarchy: Parent → Orchestrator → Leaf → Micro-worker.

**6 Anti-Bottleneck Rules (B1-B6):**
```
B1 — Mini-batch: max 5 leaf workers per orchestrator batch (not all at once)
B2 — Depth auto-limit by Tier: T1-2→1 level, T3→2 levels, T4→3 levels (only if >50 files)
B3 — Context snapshot: <200 token snapshot injected into every subagent
B4 — Retry degradation: retry 2 = inline by leaf, retry 3 = orchestrator does it inline
B5 — Aligned timeouts: micro 60s → leaf 120s → orch 240s → parent 300s
B6 — can_dispatch() mandatory before every batch (see Phase 3d)
```

**Leaf Dynamic Split:** a leaf that evaluates its task as too complex (3+ files with dependencies, estimate >120s) can spawn MAX 2 micro-workers. Micro-worker is dead-end (cannot spawn further). Context snapshot injected. If both fail → leaf implements inline (B4).

### 2b — Streaming Dispatch (wave-based)

Instead of one big `delegate_task(tasks=[...])` and waiting for ALL results, use a **streaming** approach:

```
┌─ Decompose goal into 50 tasks
├─ Dispatch BATCH 1: tasks 1-25 (subagents 1-25)
├─ WHILE batch 1 runs:
│   ├─ Prepare BATCH 2: tasks 26-50
│   ├─ On first result from BATCH 1 → evaluate IMMEDIATELY
│   │   ├─ score >= threshold? → ✅ done
│   │   └─ score < threshold? → retry IMMEDIATELY (don't wait)
│   ├─ Dispatch BATCH 2: tasks 26-50
│   └─ Continue processing results streaming
└─ Retries interleave naturally with the flow
```

**Advantage:** zero dead time between batches. Retries start while other tasks are still running.

**⚠️ Safety limit:** every batch MUST pass `can_dispatch()` (Phase 3d) before starting. If context budget is at risk, the batch is auto-reduced — does NOT suspend streaming, just launches smaller batches until budget frees up.

### 2c — Subagent Prompt Template (self-aware)

Every subagent knows it's part of a larger loop:

```
TASK: {description}
YOUR ID: {task_id}
QUALITY THRESHOLD: {threshold}/10
MAX_INTERNAL_ITERATIONS: 3

QUALITY CRITERIA:
{custom_criteria}

SELF-AWARENESS:
You are one of {total_tasks} parallel agents working on {goal_name}.
Others are working on related but non-overlapping files.
Your work will be evaluated automatically when you return.
If you score below threshold, you WILL be retried with feedback.

INSTRUCTIONS:
1. Implement the task completely (no stubs, no TODO, no pass)
2. Self-verify against quality criteria
3. If below threshold, fix and re-verify (max 3 tries)
4. If still below threshold after 3 tries, return honest score + gaps

RETURN FORMAT (MANDATORY at end):
## RESULT
- task_id: {task_id}
- status: pass|fail|partial
- quality_score: N/10
- gaps: [specific gaps if any]
- files_created: [paths]
- notes: [anything I should know]
```

### 2d — Streaming Gather

```
while goal_not_achieved AND iteration < max:
  result arrives from subagent X
  parse: status, score, gaps, files_created
  validate: files exist (stat), no stubs (grep TODO/pass)
  
  if score >= threshold:  → mark complete
  if score < threshold:   → IMMEDIATE RETRY with specific feedback
                           (don't wait for other results)
  
  update first_pass_rate, avg_quality
  
  if ALL accounted for AND all passed:
    🎉 GOAL ACHIEVED
```

### 2e — Pre-Dispatch Validation

```
□ Each task has DIFFERENT files (no conflicts)
□ Each task has specific quality criteria
□ Load balanced (no task > 2× average)
□ Task count <= available subagents
□ Retry templates ready
□ Interface contracts documented for communicating modules? (Phase 1d)
□ Assembly task planned for shared files? (Phase 3g)
□ can_dispatch() passed? (Phase 3d — context budget check)
```

---

## Phase 3 — Streaming Quality Gate

### 3a — Security Shield AUTO (regex-based, ALL tiers)

**Applied to ALL code-producing tasks, even Tier 1.** If a check fails → immediate retry with specific feedback.

```
SECURITY AUTO CHECK (run after file validation, before quality gate):

1. ZERO HARDCODED SECRETS (CRITICAL — blocks task):
   ├─ Regex: \b(api_key|password|secret|token|api_secret)\s*=\s*['\"][^'\"]{8,}
   │          WITHOUT os.getenv / env / process.env in next 3 lines
   ├─ Blocks: "API_KEY = 'sk-abc123...'", "password = 'admin'"
   ├─ OK:     "API_KEY = os.getenv('API_KEY')", "password = get_secret()"
   └─ If found → ❌ RETRY: "Move credential to environment variable"

2. SQL INJECTION RISK (HIGH — blocks task):
   ├─ Regex: (f['"]SELECT|f['"]INSERT|\.format\(.*SELECT|\+ .*SELECT|execute\(.*\+)
   ├─ Blocks: f"SELECT * FROM users WHERE id={user_id}"
   │          "SELECT * FROM " + table_name
   ├─ OK:     cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
   │          session.query(User).filter(User.id == user_id)  [ORM]
   └─ If found → ❌ RETRY: "Use parameterized queries or ORM, never f-string SQL"

3. PLACEHOLDER SECRETS (warning — doesn't block):
   ├─ Regex: \b(API_KEY|TOKEN|SECRET)\s*=\s*(['"]\s*['"]|None|''|"")\s*#\s*TODO
   └─ If found → ⚠️ WARNING (may be intentional)
```

### 3b — Physical File Validation (MANDATORY for Tier 2-4)

**Not optional anymore.** Every code-producing task MUST pass this before being marked complete. Doc/config tasks → skip.

```
VALIDATE RESULT (mandatory for code tasks):
1. read_file(task.files_created[0]) — exists? → if not, ❌ fail immediate
2. grep -n "TODO\|pass\|stub" task.files_created — dead code? → ❌
3. python -c "from task.module import ..." — syntax ok? → ❌
4. wc -l task.files_created — file not empty? → ❌
```

If physical validation fails → **immediate retry with specific feedback** (no silent failure).

### 3c — Execution Reality Check (for standalone scripts and tests)

For **standalone scripts, pure functions, or unit tests**, run the code in sandbox:

```
EXECUTION CHECK (only for sandboxable tasks):
1. Run pytest test_file.py or python script.py in sandbox
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

When dispatching 30-100 subagents, each returns a summary. **100 simultaneous summaries can saturate the parent context window** and trigger compression death spiral.

```
CONTEXT BUDGET RULES:
1. Before dispatching a large batch (Tier 3+):
   ├─ Calculate context budget: context_length - (system_prompt + conversation_so_far)
   ├─ Estimate summary size: N_subagents × ~2000 tokens avg per summary
   └─ If N_subagents × 2000 > context_budget × 0.6:
      └─ ⚠️ TOO MANY SUBAGENTS FOR REMAINING CONTEXT
      └─ Reduce batch size (dispatch in 2-3 waves, not all at once)
      └─ Or reduce summary target: instruct subagents to return <500 token summaries

2. Wave dispatch (if batch > 20 subagents):
   ├─ Wave 1: tasks 1-20 → collect results → process → free context
   ├─ Wave 2: tasks 21-40 → collect → process → free context
   └─ Wave 3: tasks 41-N → ...
   └─ ⚠️ Warning threshold: >20-25 simultaneous in-flight subagents with >1000 token summaries risks saturation

3. Proactive summary compression:
   ├─ Tier 2: summary <500 tokens (3-5 lines)
   ├─ Tier 3: summary <1000 tokens (5-10 lines)
   └─ Tier 4: summary <2000 tokens (10-20 lines)

4. Compression death spiral prevention:
   ├─ If context compression triggers 2+ times in one session:
   │   └─ ⚠️ CONTEXT SATURATED — reduce subagents or summary size
   │   └─ Switch to smaller wave dispatch
   └─ Never ignore compression triggers — they signal overflow
```

**Real cost of ignoring this:** 100 summaries saturate the context → Hermes compresses → loses context of completed tasks → retries duplicate already-done tasks → more summaries → overflow again → death spiral → session crashes or produces terrible quality.

### 3e — Adaptive Threshold Tuning (mid-loop, next batch only)

If too many tasks fail, **adjust decomposition for the next batch** (NOT for already-dispatched tasks):

```
MONITOR:
if first_pass_rate (after 25% of tasks) < 60%:
    └─ "Decomposition too coarse for these tasks"
    └─ For NEXT batch: double granularity (split each task in 2)
    └─ Already-in-flight tasks complete with original granularity
    └─ Save lesson: "Task type X needs finer decomposition"

if first_pass_rate (after 25% of tasks) > 90%:
    └─ "Decomposition too fine, overhead excessive"
    └─ For NEXT batch: merge adjacent tasks
    └─ Save lesson: "Task type X can be aggregated"
```

**⚠️ Important:** NEVER change granularity for already-dispatched tasks. Risks overlaps and conflicts with "old style" tasks still running.

### 3f — Actor-Critic Escalation Trigger (for problematic tasks only)

**Not for every task.** Activates only when a task has accumulated **3+ retries** without converging. Distinguishes between "difficult task" and "structural problem":

```
ACTOR-CRITIC CHECK (only if retry_count >= 3 for same task):
1. Analyze failure pattern:
   ├─ Same error every retry? → context problem (ambiguous instructions)
   ├─ Different errors each retry? → execution problem (unstable subagent)
   ├─ Progressive worsening? → circular learning
   └─ Stalemate (same score, same gap)? → poorly specified task

2. Action based on pattern:
   ├─ Ambiguous context → rewrite task with more precise instructions
   ├─ Unstable execution → reduce complexity (split into 2 micro-tasks)
   ├─ Circular learning → stop retry, escalate to Guardrail 2
   └─ Poorly specified task → immediate escalation to Phase 3j

3. Limit: 1 SINGLE Actor-Critic attempt per task.
   If still failing → escalation Phase 3j (no more retries).
```

### 3g — Git Commit+Push Policy (MANDATORY)

The user wants commit+push after every successful change. The loop encodes this:

```
GIT CHECKPOINT RULES:
1. After a task PASSES the quality gate (score >= threshold) and files are validated:
   └─ If task files are EXCLUSIVE (not shared) → git add + commit + push immediately
   └─ If files include SHARED files (router, __init__, config) → WAIT: commit happens only in assembly task post-batch
2. DO NOT commit files from still-in-flight tasks (potential conflicts)
3. If two completed tasks modify EXCLUSIVE files (no shared file overlap):
   └─ Separate commits, push in sequence
4. Commit message format — conventional commits in English:
   └─ feat: add Restaurant model
   └─ fix: correct date validation in reservation
   └─ test: add tests for /api/restaurants endpoint
5. If git push fails (network, auth):
   └─ Single retry, then continue loop (commit stays local)
   └─ Report in final: "N commits not pushed"
6. 🌉 ASSEMBLY TASK: after ALL batch tasks are verified, a dedicated assembly task:
   ├─ Modifies shared files (router, __init__, config, requirements.txt)
   ├─ 🔍 DRY CHECK (Tier 3-4): scan modules for duplicate helpers/logic. Extract to shared file (utils/helpers.py or config/constants.py)
   ├─ Commits + pushes shared files (including new utils files from DRY check)
   └─ This is the ONLY task authorized to modify shared files
```

**Why in the loop and not at the end:** granular commits after every task = rollback possible for single task if a later task breaks it. Single final commit = all-or-nothing.

### 3h — Retry Intelligence

| Type | Score | Cause | Strategy |
|------|-------|-------|----------|
| **Superficial** | 5-6 | Criteria not read, minor gaps | Same task + feedback |
| **Structural** | 3-4 | Wrong approach | Redefine + architectural hint |
| **Critical** | 0-2 | Bad spec, file conflicts | Rewrite, split into micro-tasks |
| **Silent** | N/A | Timeout/no return | Pivot inline |

### 3i — Convergence-Based Limits

```
if score improved ≥ 2 points after retry:
  → continue retrying (converging)
elif score improved < 2 points:
  → change strategy (split task, give better hints)
elif score WORSENED:
  → stop retry, restart with smaller task
```

### 3j — Escalation Ladder

```
1. Self-verify (subagent) — failed
2. Retry with feedback (me) — failed
3. Change strategy (split/hint) — failed
4. ESCALATE TO USER with specific gaps and quality score
5. User decides: skip / accept with gap / manual fix
```

**Rule:** never reach step 4 without trying at least 3 different strategies.

---

## Phase 4 — Self-Learning Loop

### 4a — Pattern Capture (3-Level Persistence)

After every execution, save patterns at 3 levels:

#### Level 1 — Compressed Memory Entry (last batch of session)

Short and dense, injected into every future session. **Max 200 characters.**

```python
memory(action="add", target="memory", content=(
    f"ES[{goal_type}|T{tier}] FPR={first_pass_rate:.0%} dec={decomposition_pattern} "
    f"q={avg_quality:.1f} iter={convergence_iterations} "
    f"L: {'; '.join(lessons[:2])}"
))
```

**Example (156 chars):**
```
ES[api_crud|T3] FPR=84% dec=per_endpoint q=8.7 iter=3 L: services FPR<API; per_file ok up to 30 tasks
```

**Why compressed:** memory store is limited (2200 chars total). Verbose entries fill the budget fast.

#### Level 2 — Pattern Cache File (for successful patterns, FPR > 70%)

Detailed patterns in a local JSON file. **Zero token cost** (not in context), consultable on-demand.

```json
{
  "goal_type": "api_creation", "tier": 3,
  "total_tasks": 50, "first_pass_rate": 0.84, "avg_quality": 8.7,
  "convergence_iterations": 3,
  "lessons": ["Task type X needs finer decomposition"],
  "decomposition_pattern": "per_endpoint"
}
```

**When to consult:** at Phase 1 start, if goal_type matches a cached pattern with FPR > 80%, use it as template instead of decomposing from zero. Saves ~1500-3000 tokens.

#### Level 3 — Dedicated Skill (recurring pattern, 3+ occurrences)

If the same goal_type appears 3+ times with FPR > 75%, the pattern is stable and deserves a skill:

```python
skill_manage(
    action="create",
    name=f"pattern-{goal_type}",
    category="software-development",
    content=generate_skill_from_pattern(pattern_data)
)
```

### 4b — Adaptive Calibration

```python
def calibrate(history):
    if len(history) < 3: return defaults()
    avg = mean(h.first_pass_rate for h in history[-3:])
    if avg < 0.6:  return {"granularity": "fine", "threshold": threshold - 0.5}
    if avg > 0.95: return {"granularity": "coarse", "subagents": subagents * 0.7}
    return {"granularity": "balanced"}
```

### 4c — Token-Efficient Recall (pre-loop sequence)

At the start of every coding session, before Phase 0, run a **rapid recall**:

```
RECALL SEQUENCE (~1000 tokens):

1. Memory injection (automatic, zero extra cost)
   └─ ES[...] entries are already in context
   └─ Scan: are there pattern matches for this goal_type?

2. Pattern cache check (1 read_file call)
   └─ read_file(~/.hermes/pattern_cache.json)
   └─ Match for goal_type? → use as template

3. Skill list check (1 skills_list call)
   └─ Does "pattern-{goal_type}" skill exist?
   └─ If yes → load with skill_view (optimized structure)

4. Dynamic Knowledge check (1-2 read_file calls):
   ├─ Read ./.hermes/local-patterns.md (if exists in current project, ~200 tokens)
   ├─ Read ~/.hermes/references/dynamic-patterns.md filtered for goal technologies (~300 tokens)
   └─ Inject relevant rules as extra_criteria in subagents
```

**Token savings:** without recall: ~3000-5000 tokens creative decomposition. With recall + match: ~800-1200 tokens template adaptation = **60-75% planning token savings**.

### 4d — Self-Learning Feedback Loop (cross-session)

Complete learning cycle:

```
Session N:
  ├─ RECALL: read pattern cache + memory → use template if match
  ├─ EXECUTE: loop with calibrated parameters
  ├─ CAPTURE: save pattern (Level 1 memory + Level 2 cache)
  └─ CALIBRATE: update parameters for next use
      │
      ▼
Session N+1:
  ├─ RECALL: find Session N pattern → adapt
  ├─ EXECUTE: with calibrated parameters → FPR should improve
  ├─ CAPTURE: compare with Session N, save delta
  └─ CALIBRATE: refine further
      │
      ▼
Session N+3:
  └─ If pattern stable (FPR > 75% for 3 times) → create skill (Level 3)
```

**Measurable:** first-pass rate MUST increase over time. If after 5 sessions of the same goal_type FPR hasn't improved by at least 10%, self-learning isn't working — re-evaluate lesson format.

### 4e — Self-Learning Guardrails (CRITICAL)

Self-learning **without guardrails is dangerous**. The model learning from its own outputs can enter negative feedback cycles, accumulate bad lessons, and saturate the memory store. These guardrails are **non-optional**.

#### Guardrail 1 — Memory Budget Cap

```
BEFORE saving a memory entry:
  ├─ Count how many ES[...] entries already exist in memory
  ├─ If > 8 ES[...] entries:
  │   └─ Find oldest ES[...] entry with lowest FPR
  │   └─ Replace it (memory action="replace")
  │   └─ DON'T add — replace
  ├─ If <= 8 ES[...] entries:
  │   └─ Add new entry
  └─ Never exceed 10 ES[...] entries total
```

#### Guardrail 2 — Lesson Validation (anti-circularity)

A lesson is valid ONLY if:

```
✅ VALID (save):
   ├─ Lesson confirmed by a failed test + successful fix (evidence-based)
   ├─ Lesson is a verifiable technical pitfall (e.g. "FastAPI route ordering")
   └─ Lesson comes from a post-mortem with identified root cause

❌ INVALID (don't save — circularity risk):
   ├─ "I tried X and it worked" — not a lesson, an anecdote
   ├─ "Model X is better than Model Y" — opinion, not fact
   ├─ Self-referential lessons (e.g. "save lessons frequently")
   └─ Lessons without objective verification criteria
```

**Anti-circularity test:** before saving a lesson, ask "If this lesson were wrong, how would I know?" If no answer, don't save it.

#### Guardrail 3 — Skill Mutation Protection

```
✅ ALLOWED (no user confirmation needed):
   ├─ Patch pitfalls section (add discovered pitfalls)
   ├─ Patch references (add a reference file)
   └─ Patch examples (update obsolete examples)

⛔ FORBIDDEN (without user confirmation):
   ├─ Modify the Philosophy section
   ├─ Modify Tier thresholds
   ├─ Modify Quality criteria bases
   ├─ Delete loop phases (Phase 0-11)
   └─ Modify these guardrails themselves (meta-modification)

📋 Procedure for allowed mutations:
   1. Backup: copy original section as comment in file
   2. Patch: apply change
   3. Verify: reload skill with skill_view, verify consistency
   4. Log: save in memory "ES skill patch: <what changed and why>"
   5. Max 1 patch per session (no batch mutation)
```

#### Guardrail 4 — Skill Proliferation Cap

```
SKILL CREATION LIMITS:
  ├─ Max 5 pattern-* skills total (over limit → offer user to consolidate)
  ├─ Before creating pattern-X skill, verify no similar skill exists
  ├─ If 2 pattern-* skills have >70% similar goal_type → CONSOLIDATE into one
  ├─ Max 1 skill created per session
  └─ Each pattern-* skill must have "last_used" timestamp — if unused for 30 days → archive
```

#### Guardrail 5 — Pattern Cache Cleanup

```
PATTERN CACHE MAINTENANCE (every 10 completed batches):
  ├─ Read pattern_cache.json
  ├─ Count total entries
  ├─ If > 20 entries:
  │   └─ Sort by timestamp
  │   └─ Remove 5 oldest (save their patterns as compressed memory entry first)
  ├─ If > 50 entries:
  │   └─ EMERGENCY: remove all except 10 most recent with FPR > 70%
  └─ If a goal_type has 3+ entries with FPR < 60%:
      └─ Delete that goal_type from cache — pattern doesn't work
```

#### Guardrail 6 — Project Isolation (anti-contamination)

Lessons from one project must NOT contaminate different projects:

```
PROJECT ISOLATION RULES:
  ├─ LEVEL 1 — Memory Store:
  │   ├─ Architecture/structure lessons are PROJECT-SPECIFIC
  │   ├─ Mark with prefix: ES[goal_type|ProjectName|Tier]...
  │   ├─ During recall, skip entries that don't match current project
  │   └─ Example: ES[api_crud|PolimarketWeather|T3] FPR=84%...

  ├─ LEVEL 2 — Dynamic Knowledge Files:
  │   ├─ Style/architecture/convention lessons are LOCAL
  │   ├─ Write to ./.hermes/local-patterns.md in the repository
  │   ├─ Pure technology lessons (API, framework) are GLOBAL
  │   └─ Write to ~/.hermes/references/dynamic-patterns.md

  └─ "When in doubt, LOCAL": isolate the lesson in the current project
```

#### Guardrail 7 — Human Checkpoint (no fully autonomous skill mutation)

```
HUMAN CHECKPOINT for skill operations:
  ├─ skill_manage(action="create") → ask user confirmation first
  ├─ skill_manage(action="delete") → ask user confirmation ALWAYS
  ├─ skill_manage(action="edit") → only if user approved in this session
  ├─ skill_manage(action="patch") → allowed for pitfalls/references (Guardrail 3), but:
  │   └─ Notify user: "Patched <skill> for <reason>"
  └─ skill_manage(action="write_file") → like patch, notify after
```

**Exception — Dynamic Knowledge Expansion (Phase 4f):** writing to dynamic knowledge files is **captured knowledge, not modified behavior**. These files do NOT require human checkpoint:
- `~/.hermes/references/dynamic-patterns.md` and `./.hermes/local-patterns.md` marked `[Auto]` → autonomous ✅
- `SKILL.md` or non-`[Auto]` references → needs human OK ⚠️
- Creating/modifying skills → needs human OK 🛑

#### Guardrail 8 — Session Memory Flush Cap

```
SESSION MEMORY CAP:
  ├─ Max 3 memory entries per session
  ├─ Max 1 skill patch per session
  ├─ Max 1 pattern_cache.json update per session (last batch only)
  └─ If session produces more data than this:
      └─ Save only top-N by impact (sort by severity × FPR delta)
      └─ Rest go in final report as "lessons not persisted (cap reached)"
```

#### Guardrail 9 — Drift Detection

```
DRIFT DETECTION (every 5 sessions of same goal_type):
  ├─ Compare FPR of last 5 sessions vs previous 5
  ├─ If average FPR dropped > 10%:
  │   └─ ⚠️ DRIFT DETECTED — self-learning is degrading
  │   └─ Actions:
  │       ├─ Stop saving new lessons for this goal_type
  │       ├─ Alert user: "Pattern for X is degrading, suspicious lessons"
  │       └─ Propose reset of lessons for that goal_type
  └─ If average FPR is stable or improved:
      └─ ✅ Self-learning healthy, continue
```

#### Guardrail 10 — Transparency Log

Every self-learning operation must be traceable:

```
SELF-LEARNING LOG (in final report of every session):
  ├─ Memory entries saved: N (of which N replaced)
  ├─ Pattern cache: updated/not updated (reason)
  ├─ Dynamic patterns: global N new, local N new
  ├─ Skill patched: yes/no (which, what, why)
  ├─ Skill created: yes/no (which, with user confirmation?)
  ├─ Lesson validation: N validated, N rejected (rejection reason)
  └─ Guardrails activated: list of guardrails that limited operations
```

**The user must always know what was learned, what was modified, and what was blocked.**

### 4f — Dynamic Knowledge Expansion (post 3+ retry) — Local/Global Split

**Trigger:** a task required **3 or more retries** to pass the quality gate. This indicates knowledge worth capturing — a deprecated API, a broken pattern, a context gap.

```
DYNAMIC KNOWLEDGE EXPANSION:
1. Extract the resolution rule:
   ├─ What failed? (API, pattern, syntax, library)
   ├─ Why did it fail? (deprecation, breaking change, context gap)
   └─ What's the solution? (the specific pattern that worked)

2. Classify SCOPE and write to correct file:
   ├─ 🌍 GLOBAL SCOPE (Pure technology — Languages, Frameworks, Public APIs):
   │   ├─ Criterion: lesson applies to ANY project using that technology
   │   ├─ Write to ~/.hermes/references/dynamic-patterns.md
   │
   ├─ 📁 LOCAL SCOPE (Project architecture — Conventions, structure, internal wrappers):
   │   ├─ Criterion: lesson applies ONLY to this specific project
   │   └─ Write to ./.hermes/local-patterns.md (create if not exists)
   │
   └─ ⚠️ DEFAULT: when in doubt → LOCAL. A local pattern in another project is harmless noise. A global pattern where it doesn't belong is damage.

3. Auto-load in future tasks (Tier 2-4):
   ├─ ALWAYS read ./.hermes/local-patterns.md (if exists in current project)
   ├─ Read ~/.hermes/references/dynamic-patterns.md ONLY for technologies mentioned in goal
   └─ Inject relevant rules as extra_criteria in subagent contexts
```

### 4g — Lesson Hierarchy (which lessons to save)

Not all lessons have equal value. Prioritize:

```
LESSON PRIORITY (save only top 2-3 per batch):

P0 — Structural (always save):
  "Per-file decomposition doesn't work for tasks with circular dependencies"
  → Changes future decomposition strategy

P1 — Task-specific (save if recurring):
  "Service tasks (notifications/payments) have 20% lower FPR"
  → Add extra quality criteria for services

P2 — Context-specific (save if project recurring):
  "FastAPI route ordering: static routes before /{param}"
  → Pitfall to check in similar FastAPI projects

P3 — One-off (DON'T save, log only in STATE):
  "Module XYZ had a typo in the name"
  → Not a lesson, an isolated incident
```

**Rule:** saving everything = memory overflow + useful lessons drowned by noise. Less but better.

### 4h — Skill Self-Improvement

- If a decomposition pattern succeeds 3+ times → save as reusable pattern
- If a pitfall is discovered → add to pitfalls section (general, not project-specific)
- Each self-improvement action bumps the skill version:
  - Patch fix (v5.2) → new pitfall or minor calibration
  - Minor improvement (v5.5) → new pattern or phase
  - Major rewrite (v6.0) → breakthrough architecture change

---

## Phase 5 — Final Report

```
## ✅ [Goal]

### Loop Efficiency
├─ Subagents: N / M | First-pass: XX% | Convergence: X iter
├─ Quality: X.Y/10 | Duration: X min
├─ Streaming retry: X immediate, Y batch

### Self-Learning
├─ Pattern saved: decomposition_pattern (XX% first-pass)
├─ Lesson: [lesson learned]
├─ Calibration: [parameter changes]
├─ Guardrails activated: [list]
└─ Skill: v5.x (improved by: [reason])

### Quality
├─ ✅ Passed: X
├─ ⚠️ Gaps accepted: Y (details: ...)
└─ ❌ Escalated: Z

### Self-Feedback
├─ Self-assessment: XX/100
└─ Notes: [strengths and improvement areas]
```

---

## Phase 6 — Quality Matrix

### Quality Scoring Rubric

Objective criteria for scoring subagent output (0-10). Every score MUST have a rationale.

| Score | Label | Criteria | Action |
|-------|-------|----------|--------|
| **10** | Flawless | Production-ready, all edge cases, tests pass, docs complete, no TODOs | Accept |
| **9** | Excellent | Minor polish needed (comment, naming), all requirements met | Accept |
| **8** | Good | Functional, all requirements met, minor gaps (missing error path, no tests) | Accept |
| **7** | Solid | All core requirements met, some edge cases missing, basic error handling | Accept |
| **6** | Adequate | Core works but superficial: missing validation, limited edge cases | Retry with feedback |
| **5** | Weak | Requirements partially met, gaps in logic, no error handling, stubs found | Retry with feedback |
| **4** | Poor | Wrong approach, structural issues, doesn't handle basic cases | Redefine + hints |
| **3** | Bad | Most requirements missed, broken logic, file conflicts | Redefine + split |
| **2** | Critical | Spec not followed, doesn't compile/run, critical gaps | Rewrite from scratch |
| **1** | Broken | Gibberish output, empty file, hallucinated API | Escalate |
| **0** | Silent | Timeout, no return, empty response | Pivot inline |

**Scoring rules:**
- Score = base (completeness) + bonus (edge cases, error handling, tests) − penalty (stubs, conflicts, missing validation)
- Default threshold by tier: Tier 1=6, Tier 2-3=7, Tier 4=8
- If score is ambiguous, prefer the LOWER bound (strict)
- Silent failures (score 0) trigger immediate pivot — do not retry

### Per Task
- [ ] All requirements implemented (no stubs, TODO, pass)
- [ ] Edge cases covered (empty, null, duplicate, error, limit)
- [ ] Error handling present
- [ ] Project conventions respected
- [ ] Security Shield passed (no hardcoded secrets, no SQL injection) — Phase 3a
- [ ] Physical files validated (exist, non-empty, no stubs) — Phase 3b

### Per Batch
- [ ] All subagents delivered? (no silent failures)
- [ ] All declared files exist? (physical verification)
- [ ] No conflicts between modified files?
- [ ] No orphaned code or duplicates?
- [ ] Context window not saturated? (can_dispatch check passed)
- [ ] Git checkpoint done for exclusive files?

### Per System
- [ ] First-pass rate calculated and saved
- [ ] Average quality documented
- [ ] Decomposition pattern captured
- [ ] Calibration updated
- [ ] Guardrails activated logged
- [ ] Loop ended because goal achieved, not timeout

---

## Phase 7 — Self-Execution Infrastructure

The loop is powered by supporting files in the skill directory. These make the methodology executable, not just descriptive.

### 7a — Pattern Persistence (SQLite MCP)

The self-learning loop stores patterns in the Hermes SQLite database via the `sqlite` MCP server.

**Schema:** `references/pattern-store.sql` defines tables for executions, decomposition patterns, pitfalls, and calibrations.

**Pattern capture flow:**
```sqlite
-- After each execution, log the run:
INSERT INTO executions (goal, goal_type, tier, total_tasks, first_pass_rate, avg_quality, convergence_iterations, decomposition_pattern, lessons)
VALUES ('...', 'api_creation', 3, 50, 0.84, 8.7, 3, 'per_endpoint', '[Task type X needs finer decomposition]');

-- If a decomposition pattern succeeded 3+ times, register it:
INSERT INTO decomposition_patterns (name, description, granularity, subagent_range_min, subagent_range_max, sql)
VALUES ('per_endpoint', 'One subagent per API endpoint', 'fine', 15, 50, 'SELECT ...');
```

**Calibration queries:**
```sqlite
-- Get last 3 first-pass rates for adaptive calibration:
SELECT first_pass_rate FROM executions ORDER BY id DESC LIMIT 3;

-- Find best decomposition pattern for a goal type:
SELECT name, success_rate FROM decomposition_patterns ORDER BY success_rate DESC LIMIT 5;
```

**Viewing stored patterns:** use `mcp__sqlite__read_query` with the schema as reference.

### 7b — Bootloader Script

The bootloader at `scripts/init-state.sh` initializes the STATE object:

```bash
# Initialize state for a new goal:
bash scripts/init-state.sh "Deploy microservice to staging"
```

The script auto-detects tier from goal characteristics, sets threshold based on tier, and prints a JSON STATE for the agent to adopt.

### 7c — MCP Integration

The loop leverages available MCP servers for context and persistence:

| MCP Server | Tool | Phase | Usage |
|-----------|------|-------|-------|
| **sqlite** | `read_query`, `write_query` | Phase 4, 7a | Pattern persistence, calibration queries |
| **graphify** | `query_graph`, `get_node`, `shortest_path` | Phase 0b | Codebase context, dependency analysis |
| **sequential-thinking** | `sequentialthinking` | Phase 1, 3f | Complex reasoning, Actor-Critic analysis |
| **github** | `get_file_contents`, `create_or_update_file`, `push_files` | Phase 7e | GitHub sync, code review |

### 7d — Cron Integration (Scheduled Loop)

The loop can run on a schedule via Hermes cron, enabling autonomous monitoring and maintenance:

```yaml
# Example: Daily codebase health scan
cronjob:
  schedule: "0 6 * * *"
  prompt: "Run elysium-swarmloop: scan codebase for technical debt, generate report"
  skills: ["elysium-swarmloop"]
```

Use cases:
- **Daily health scan** — check code quality, test coverage, dependency drift
- **Weekly refactor** — identify and fix technical debt
- **On-demand deploy** — trigger deployment pipeline via webhook

### 7e — GitHub Sync

This skill lives at [github.com/Boschi404/Elysium-Swarmloop](https://github.com/Boschi404/Elysium-Swarmloop). Improvements should be pushed back:

```bash
git add -A
git commit -m "v0.6 — description of improvement"
git push origin main
```

The skill is public (MIT license). Every meaningful improvement bumps the version.

---

## Phase 10 — Skill Ecosystem Integration

Elysium doesn't work in a vacuum. These complementary skills should be loaded and referenced during the loop:

| Loop Phase | Skill to Load | Why |
|-----------|---------------|-----|
| Phase 1 (Decompose, logic tasks) | `test-driven-development` | Every code task should follow RED→GREEN→REFACTOR. Include "write tests first" in quality criteria |
| Phase 3 (Validation) | `verification-strategies` | When no test suite exists or environment can't run tests. Verify with curl, type checks, import checks |
| Phase 3 (post-batch, before git push) | `requesting-code-review` | Pre-commit review: security scan, quality gates, auto-fix |
| Phase 3j (Escalation, level 1) | `systematic-debugging` | When a task doesn't converge after 3 retries, do root-cause analysis instead of blind retry |
| Phase 3j (Escalation, level 2) | `post-mortem` | If escalation continues after systematic-debugging, structured 5 Whys + regression test + memory feed |
| Post-batch (Tier 3+ complete) | `deploy-release` | Version bump, changelog, git tag, deploy + health check + rollback plan |

**Integration in the loop:**
```
DURING DECOMPOSITION (Phase 1):
  └─ For code tasks:
     └─ Quality criteria: "Follow TDD: test first, then implementation"
     └─ Subagent context: "Load test-driven-development skill"

DURING STREAMING GATHER (Phase 3):
  └─ For file validation:
     └─ If test suite exists: pytest -q
     └─ If NOT or environment broken: load verification-strategies
        └─ Verify with: import check, curl endpoint, type stub check

AFTER BATCH COMPLETE, BEFORE GIT PUSH:
  └─ Load requesting-code-review
     └─ Security scan + quality gates + auto-fix

DURING ESCALATION (Phase 3j):
  └─ Level 1 (3 retries failed): load systematic-debugging
     └─ 4-phase root cause: understand → isolate → fix → verify
  └─ Level 2 (level 1 fails): load post-mortem
     └─ 5 Whys + regression test + memory feed
```

---

## Phase 11 — Long Session Management

**For sessions 2h+ with 30+ turns.** Context grows, quality degrades, architectural decisions are forgotten.

### The Problem
```
Turn 1-10:  quality 8/10 ✅
Turn 11-20: quality 7/10 ⚠️ (context at 50%)
Turn 21-30: quality 5/10 ❌ (context at 80%, compression death spiral)
```

### The Solution — 3 Mechanisms

#### 1. Session State File (on disk, not in context)

```python
# Track state and decisions to a local JSON file
sm = SessionManager("build_auth", "Implement complete JWT auth")
sm.track_turn(action="created User model", files=["models.py"], score=8)
sm.track_decision("Use JWT refresh rotation", "More secure for mobile")
```

State is saved to `~/.hermes/sessions/<id>_<turn>.json`. Never keep full history in context — just a **context summary** of ~200 tokens.

#### 2. Automatic Checkpoint

```python
# Every 8 turns or 10 minutes
if sm.should_checkpoint():
    cp = sm.checkpoint()
    # Compresses past turns, keeps only last 3 detailed
    # Saves to disk, frees memory
```

Checkpoint produces a summary like:
```
=== SESSION STATE: build_auth ===
Goal: Implement complete JWT auth
Turns: 20 | Quality: 7.7/10 (stable)
Files: models.py, routes.py, auth.py, test_auth.py
Decisions: Use JWT refresh rotation (turn 5)
Last checkpoint: turn 16
```

#### 3. Quality Trend Monitor

Detects degradation in the last 5 evaluations:

```python
# If quality_trend == "degrading" → alert + slow down
if "degrading" in sm.get_summary():
    # Reduce next task complexity
    # Take a checkpoint
    # Verify architectural decisions
```

### Interrupt Recovery

If the session is interrupted (crash, close, task switch):

```python
sm = SessionManager("build_auth", "Implement complete JWT auth")
recovery = sm.recover()
# recovery = {
#   "status": "recovered",
#   "total_turns": 20,
#   "files_created": ["models.py", "routes.py", ...],
#   "last_action": "fix typo",
#   "last_score": 8,
#   "suggestion": "You were at turn 19: 'fix typo'. Continue with..."
# }
```

### Context Summary (what goes in the prompt instead of full history)

When context is >60% saturated, instead of repeating the full history, use:

```
=== SESSION STATE: {session_id} ===
Goal: {goal}
Turns completed: {N}
Average quality: {X}/10 ({trend})
Files modified: {file1}, {file2}, ...
Architectural decisions: {N}
  - [{turn}] {decision}
Last checkpoint: turn {turn}
⚠️ Quality is degrading — simplify next tasks.
```

---

## Scripts

The skill directory includes supporting scripts:

| Script | Purpose |
|--------|---------|
| `scripts/init-state.sh` | Bootloader — initializes STATE object, auto-detects tier |
| `scripts/install.sh` | Auto-installer for the skill (bash install.sh) |

**Reference implementation for additional scripts** (create as needed):
- `scripts/session_manager.py` — SessionManager class: state tracking, checkpoint, quality trend, interrupt recovery
- `scripts/pattern_cache.json` — Local pattern cache file (created automatically)

---

## Pitfalls

### ❌ Loop not truly autonomous
If I stop to "plan" instead of decide-and-act, I'm not a loop. Decision must be: **assess → act → repeat**. Not "assess → plan → plan more → act".

### ❌ Streaming gather forgotten
If I wait for ALL results before retrying, I lose streaming advantage. Retry must start AS SOON AS a below-threshold result arrives.

### ❌ Non-adaptive decomposition
If decomposition is always the same (always 10 tasks per file), I don't leverage 100 subagents. Scale with available slots.

### ❌ Scale patterns unused
Having 100 subagents and using 10 is waste. Use multi-variant or exploration patterns to fill slots.

### ❌ Self-learning skipped
The power is that every run improves the next. If I don't save patterns and calibrate, I'm not improving.

### ❌ Quality threshold ignored
Accepting 5/10 because "it works" defeats the loop. If threshold is too high, calibrate — don't ignore.

### ❌ Escalation skipped
If a task doesn't converge and I hide it instead of escalating, the system produces low quality. Follow the escalation ladder.

### ❌ Same decomposition for all goals
A CRUD API decomposes differently from a data pipeline or a UI redesign. Use the right scale pattern.

### ❌ Not processing during dispatch
If I dispatch 100 tasks and sit idle, I waste minutes. While subagents run: prepare retry templates, prepare next batch, analyze partial results.

### ❌ Not verifying subagent output physically
Subagents can declare "files_created: [a, b, c]" but files may not exist or be empty. Verify with `read_file` or `stat`.

### ❌ State not updated between results
State (completed, failed, first_pass_rate) must update AFTER EVERY RESULT, not at batch end. Needed for streaming decisions.

### ❌ Overfitting self-learning
Saving a pattern after ONE execution risks learning from outliers. Need 3+ similar confirmations before consolidating.

### ❌ "Autonomous" ≠ "no supervision"
Autonomous = decide alone, but DOCUMENT everything. The user must see WHAT was decided and WHY. Final report is mandatory.

### ❌ Tier 4 for Tier 1 tasks
Don't run the full loop for "change one line in config.yaml". Fast path exists for a reason.

### ❌ Context window overflow — 100 summaries saturate the parent
Dispatching 100 subagents means 100 summaries in the parent context. With `max_summary_chars: 24000`, 100 × 2000 tokens = 200K tokens of summaries. **This saturates the context window and causes compression death spiral.**

**Solution (Phase 3d):** wave dispatch (max 20-25 simultaneous for Tier 3+), proactive summary compression, monitor compression triggers.

### ❌ Security vulnerabilities in subagent output
Subagents can introduce hardcoded API keys or SQL injection vulnerabilities without the main agent noticing. **Always run Security Shield AUTO (Phase 3a)** before accepting any result.

### ❌ No guardrails on self-learning
Self-learning is powerful but **dangerous without guardrails**. Risks: memory overflow, circular learning, skill drift, project contamination.

**Solution:** Guardrails in Phase 4e are NON-OPTIONAL. Self-learning is autonomous in DETECT (what to learn) but collaborative in ACT (structural changes need human consent).

### ❌ Not using the Quick Start
The Quick Start shows the loop in 7 steps. If unsure what to do, return to it and ask "what step am I in?"

### ❌ Depth-2 orchestrator used as leaf
When using `role="orchestrator"`, the subagent MUST decompose and delegate. If it does all work itself, depth-2 is wasted. Always spawn leaf workers for independent subtasks.

### ❌ Orchestrator does no quality gate
An orchestrator that spawns workers and just concatenates results is a passthrough. The orchestrator MUST evaluate worker output, retry failures, and synthesize.

### ❌ Skill self-modification adds project-specific trivia
This skill is a **general workflow engine**. Every edit must improve the autonomous workflow, not add framework-specific bugs, dependency issues, or error messages from one project. If a project-specific lesson is valuable enough to keep, it becomes a SEPARATE skill, not part of this one.

### ❌ No tier fast-path for trivial tasks
Running the full loop for a single-line change wastes subagents and degrades signal. Always check: is this Tier 1? If yes, fast-path it.

### ❌ Quality score without rationale
Scoring 6/10 without documenting WHY is useless for retry. Every score must name the specific gap (missing edge case X, no error handling for Y).

### ❌ Pattern captured but never queried
Saving patterns to sqlite is only useful if the next execution queries them. Phase 0b step 6 must actually SELECT from the pattern store.

### ❌ No MCP fallback
If the sqlite MCP server is down, self-learning should degrade gracefully — log to a local JSON file as fallback, don't block the loop.

### ❌ Cron loop without recovery
A scheduled swarmloop that fails should not retry forever at cron level. Use `repeat: 1` for one-shot or implement circuit breaker after 3 consecutive failures.

### ❌ Function signature mismatch between parallel subagents
Subagent A produces `router.py` that calls `build_prompt(...)`, subagent B produces `client.py` that defines `build_prompt(...)`. If signatures don't match (different params, one uses `await` and the other doesn't), code breaks silently. **Solution:** Shared Interface Contracts (Phase 1d) — the exact signature must be in both subagents' prompts.

### ❌ 4-Band Filter ignored for simple requests
Skipping the 4-Band Filter for what looks like a simple request risks loading the full skill (8K tokens wasted) for a one-line change. Always check the band first.

---

## Version History

```
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
v5.0.0 — Elysium Swarmloop: rebranded from agentic-auto-pilot,
         cleaned project-specific pitfalls, added depth-2 orchestration,
         self-improvement guardrails, version bump discipline.
v4.0.0 — Autonomous loop engine, streaming gather, self-learning
v3.0.0 — Scatter-gather + quality threshold loop
v2.0.0 — Multi-agent parallel execution
v1.0.0 — Original guided workflow
```
