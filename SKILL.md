---
name: elysium-swarmloop
description: "The Self-Improving Multi-Agent Orchestration Engine. Always-on autonomous agentic loop: prompt enhancement → deep research → massive scatter-gather (up to 100 subagents) → streaming quality gate (immediate retry on arrival) → self-learning iteration → loop until goal achieved with zero human intervention. Auto-activates on EVERY prompt."
version: 5.0.0
author: Hermes Agent + Boschi404
tags: [agentic, auto, workflow, multi-agent, quality, research, iteration, scatter-gather, streaming-gather, self-learning, autonomous-loop, meta-scaling, orchestrator-depth2, self-improving, swarmloop]
---

# Elysium Swarmloop
The Self-Improving Multi-Agent Orchestration Engine
*Towards Agentic Utopia.*

## Philosophy

**I don't follow a workflow. I am the loop. And I improve myself.**

Elysium Swarmloop is a self-improving autonomous orchestration engine that:

1. **Decides what to do next** — state machine, not recipe
2. **Executes at any scale** — 1 to 100 subagents per batch
3. **Orchestrates hierarchically** — depth-2: orchestrators spawn workers
4. **Evaluates and retries instantly** — streaming gather, no batching delay
5. **Learns and evolves** — captures patterns, calibrates, bumps version on improvement

**Guardrails for self-modification:**
- Every edit to this skill must **improve the autonomous workflow**, not add project-specific trivia
- No project error messages, framework-specific bugs, or dependency issues
- Each modification increments the PATCH version (v5.x), meaningful improvements bump MINOR (v5.x), breakthrough rewrites bump MAJOR (v6.0.0)
- When version bumps, the skill's own `# Changelog` section at the bottom gets a new entry

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

```
STATE = {
  goal, tier, threshold, subagents_available: 100,
  completed: [], failed: [], in_flight: [],
  iteration: 0, max_iterations, first_pass_rate, avg_quality,
  self_lessons: [], start_time
}
```

### 0b — Assess (after every event)

```
ASSESS:
1. Completed? (tasks_completed)
2. Failed? (tasks_failed + gaps)
3. In flight? (tasks_in_flight)
4. Goal reachable? (gaps vs remaining resources)
5. Adjust strategy? (first_pass_rate < 60% → finer granularity)
6. Past patterns for this task type?
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

### 1c — Dynamic Quality Criteria

```python
criteria = {"completeness", "correctness", "edge_cases"}
if task_type == "api":    criteria += {"status_codes", "validation", "tests"}
if task_type == "model":  criteria += {"constraints", "repr", "migration"}
if task_type == "ui":     criteria += {"responsive", "states", "anti-slop"}
```

---

## Phase 2 — Hierarchical Scatter (Depth-2 Orchestration)

### 2a — Two-Level Hierarchy

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

### 2b — Dispatch Strategy

```
BATCH 1: 25 leaf subagents (independent work)
WHILE batch 1 runs:
  → prepare batch 2 context
  → on first result: evaluate and retry IMMEDIATELY if below threshold
  → dispatch batch 2
  → if complex sub-task found, re-dispatch as orchestrator with depth-2 workers
```

### 2c — Streaming Gather

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

### 2d — Pre-Dispatch Validation

```
□ Each task has DIFFERENT files (no conflicts)
□ Each task has specific quality criteria
□ Load balanced (no task > 2× average)
□ Task count <= available subagents
□ Retry templates ready
```

---

## Phase 3 — Streaming Quality Gate

### 3a — Retry Intelligence

| Type | Score | Cause | Strategy |
|------|-------|-------|----------|
| **Superficial** | 5-6 | Criteria not read, minor gaps | Same task + feedback |
| **Structural** | 3-4 | Wrong approach | Redefine + architectural hint |
| **Critical** | 0-2 | Bad spec, file conflicts | Rewrite, split into micro-tasks |
| **Silent** | N/A | Timeout/no return | Pivot inline |

### 3b — Convergence-Based Limits

```
if score improved ≥ 2 points after retry:
  → continue retrying (converging)
elif score improved < 2 points:
  → change strategy (split task, give better hints)
elif score WORSENED:
  → stop retry, restart with smaller task
```

### 3c — Escalation Ladder

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

### 4a — Pattern Capture

After every execution:

```json
{
  "goal_type": "api_creation", "tier": 3,
  "total_tasks": 50, "first_pass_rate": 0.84, "avg_quality": 8.7,
  "convergence_iterations": 3,
  "lessons": ["Task type X needs finer decomposition"],
  "decomposition_pattern": "per_endpoint"
}
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

### 4c — Skill Self-Improvement

- If a decomposition pattern succeeds 3+ times → save as reusable pattern
- If a pitfall is discovered → add to pitfalls section (general, not project-specific)
- Each self-improvement action bumps the skill version:
  - Patch fix (v5.1) → new pitfall or minor calibration
  - Minor improvement (v5.5) → new pattern or phase
  - Major rewrite (v6.0) → breakthrough architecture change

---

## Phase 5 — Final Report

```
## ✅ [Goal]

### Loop Efficiency
├─ Subagents: N / M | First-pass: XX% | Convergence: X iter
├─ Quality: X.Y/10 | Duration: X min

### Self-Learning
├─ Pattern saved: decomposition_per_file (84% first-pass)
├─ Lesson: task type X needs finer criteria
└─ Skill: v5.x (improved by: [reason])

### Quality
├─ ✅ Passed: X
├─ ⚠️ Gaps accepted: Y (details: ...)
└─ ❌ Escalated: Z
```

---

## Phase 6 — Quality Matrix

### Per Task
- [ ] All requirements implemented (no stubs, TODO, pass)
- [ ] Edge cases covered (empty, null, duplicate, error, limit)
- [ ] Error handling present
- [ ] Project conventions respected

### Per Batch
- [ ] All subagents delivered? (no silent failures)
- [ ] All declared files exist? (physical verification)
- [ ] No conflicts between modified files?
- [ ] No orphaned code or duplicates?

### Per System
- [ ] First-pass rate calculated and saved
- [ ] Average quality documented
- [ ] Decomposition pattern captured
- [ ] Calibration updated
- [ ] Loop ended because goal achieved, not timeout

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
Saving a pattern after ONE execution risks learning from outliers. Need 3+ similar confirmations before固化.

### ❌ "Autonomous" ≠ "no supervision"
Autonomous = decide alone, but DOCUMENT everything. The user must see WHAT was decided and WHY. Final report is mandatory.

### ❌ Tier 4 for Tier 1 tasks
Don't run the full loop for "change one line in config.yaml". Fast path exists for a reason.

### ❌ Not using the Quick Start
The Quick Start shows the loop in 7 steps. If unsure what to do, return to it and ask "what step am I in?"

### ❌ Depth-2 orchestrator used as leaf
When using `role="orchestrator"`, the subagent MUST decompose and delegate. If it does all work itself, depth-2 is wasted. Always spawn leaf workers for independent subtasks.

### ❌ Orchestrator does no quality gate
An orchestrator that spawns workers and just concatenates results is a passthrough. The orchestrator MUST evaluate worker output, retry failures, and synthesize.

### ❌ Skill self-modification adds project-specific trivia
This skill is a **general workflow engine**. Every edit must improve the autonomous workflow, not add framework-specific bugs, dependency issues, or error messages from one project. If a project-specific lesson is valuable enough to keep, it becomes a SEPARATE skill, not part of this one.

---

## Version History

```
v5.0.0 — Elysium Swarmloop: rebranded from agentic-auto-pilot,
         cleaned project-specific pitfalls, added depth-2 orchestration,
         self-improvement guardrails, version bump discipline.
v4.0.0 — Autonomous loop engine, streaming gather, self-learning
v3.0.0 — Scatter-gather + quality threshold loop
v2.0.0 — Multi-agent parallel execution
v1.0.0 — Original guided workflow
```
