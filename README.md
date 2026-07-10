<p align="center">
  <img src="assets/logo-banner.svg" alt="Elysium Swarmloop" width="100%">
</p>

<p align="center">
  <strong>The Self-Improving Multi-Agent Orchestration Engine</strong><br>
  <em>Towards Agentic Utopia.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.6.0-d4a017?style=flat-square&labelColor=080c14">
  <img src="https://img.shields.io/badge/license-MIT-d4a017?style=flat-square&labelColor=080c14">
  <img src="https://img.shields.io/badge/subagents-100-f0d860?style=flat-square&labelColor=080c14">
  <img src="https://img.shields.io/badge/depth-2/3-ffd700?style=flat-square&labelColor=080c14">
</p>

## What is Elysium Swarmloop?

A Hermes Agent skill that transforms every prompt into an autonomous agentic workflow:

- **Massive parallelism** — up to 100 subagents per batch
- **Hierarchical orchestration** — depth-2: orchestrators spawn leaf workers
- **Streaming quality gate** — retry failures immediately, don't wait for batch completion
- **Self-learning** — captures patterns in SQLite, calibrates granularity, improves iteration after iteration
- **Zero human intervention** — the loop keeps going until the goal is achieved
- **Tier-based execution** — Tier 1 (fast-path) to Tier 4 (full epic), auto-detected

## Repository Structure

```
├── SKILL.md                    # The autonomous loop engine (v0.6.0)
├── README.md                   # This file
├── SETUP.md                    # Complete installation guide
├── assets/
│   ├── logo-banner.svg         # Banner logo (800×200)
│   └── logo-icon.svg           # Icon logo (120×120)
├── scripts/
│   ├── init-state.sh           # Bootloader — initializes STATE
│   ├── install.sh              # Auto-installer (bash install.sh)
│   └── session_manager.py      # Session state, checkpoint, interrupt recovery
└── references/
    └── pattern-store.sql       # SQLite schema for pattern persistence
```

## Core Loop

```
while goal_not_achieved:
    state = assess(goal, done, gaps)
    if state.is_done: break
    decide()         # what to do next based on state
    decompose()      # break remaining work into tasks
    scatter()        # dispatch all in parallel
    stream()         # process each result as it arrives
    learn()          # save patterns, calibrate, improve
```

## Quick Start

```bash
# Auto-install (raccomandato):
bash scripts/install.sh

# Oppure manuale:
skill_view(name='elysium-swarmloop')
```

## Required Config

```yaml
delegation:
  max_concurrent_children: 100   # up to 100 sub-agents in parallel
  max_async_children: 100        # same for async operations
  max_spawn_depth: 2             # orchestrators can spawn leaf workers
  child_timeout_seconds: 600     # enough time for complex tasks
  max_iterations: 50             # allow deep reasoning per agent
  orchestrator_enabled: true     # enable hierarchical orchestration
```

These settings are not optional tweaks.

## What's New in v0.6

- **Security Shield AUTO** — Regex-based hardcoded secret and SQL injection prevention on ALL code tasks
- **Context Window Protection** — Budget calculation, wave dispatch, summary compression, death spiral prevention
- **10 Self-Learning Guardrails** — Memory budget, lesson validation, skill mutation protection, drift detection, transparency log, and more
- **Shared Interface Contracts** — Function signatures documented pre-dispatch eliminates 90% of integration bugs
- **Actor-Critic Escalation Trigger** — Meta-evaluation after 3+ retries distinguishes task difficulty from structural problems
- **Streaming Dispatch** — Wave-based dispatch with zero dead time between batches
- **4-Band Filter** — Pre-check saves 8K tokens on simple tasks
- **Clean Code Standards** — Type hints, SRP, DRY enforcement by tier
- **Physical File Validation + Execution Reality Check** — Verify files exist, no stubs, no syntax errors, sandbox tests
- **Git Commit+Push Policy** — Auto-commit per task with assembly task for shared files
- **3-Level Pattern Capture** — Memory entry (200 chars) + JSON cache (zero token cost) + dedicated skill
- **Codebase Familiarity Override** — 50-80% subagent reduction on known codebases
- **Subagent Prompt Template** — Structured self-aware prompts with mandatory RESULT format
- **B1-B6 Anti-Bottleneck Rules** — 6 rules preventing orchestrator deadlocks
- **Phase 10 — Skill Ecosystem Integration** — Load TDD, verification, code-review, debugging skills in loop
- **Phase 11 — Long Session Management** — Checkpoints, quality trend, interrupt recovery
- **session_manager.py** — Python class for session state tracking
- **Dark + Gold SVG Logos** — New v0.6 branded assets with gold reflections

## License

MIT

## Authors

- **Boschi404** — Creator and Lead Architect
- **ffazecaldy** — Collaborator and Co-Architect
- **Hermes Agent** — Testing Agent

---

<p align="center">
  <img src="assets/logo-icon.svg" alt="ES" width="48">
</p>