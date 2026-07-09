# Elysium Swarmloop
The Self-Improving Multi-Agent Orchestration Engine

*Towards Agentic Utopia.*

**Latest version: v5.1.0**

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
├── SKILL.md                    # The autonomous loop engine (v5.1.0)
├── README.md                   # This file
├── scripts/
│   └── init-state.sh           # Bootloader — initializes STATE
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

1. Install the skill: `skill_manage(action='create', name='elysium-swarmloop', ...)`
2. Set config (see below)
3. Every prompt from then on runs through the autonomous loop

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

These settings are not optional tweaks. They are the difference between "it runs" and "it delivers production-quality results at scale." Elysium Swarmloop is designed to saturate these limits — without them, you're running a fraction of the engine.

## What's New in v5.1

- **Tier Definitions** — Clear Tier 1-4 auto-detection with fast-path for trivial tasks
- **Quality Scoring Rubric** — Objective 0-10 scoring criteria with rationale requirement
- **Phase 7 — Self-Execution Infrastructure** — Bootloader script, SQLite pattern persistence via MCP, MCP integration guide, cron scheduling
- **6 new pitfalls** — More guardrails against common failure modes

## License

MIT

## Authors

- **Boschi404** — Creator and Lead Architect
- **ffazecaldy** — Collaborator and Co-Architect
- **Hermes Agent** — Testing Agent
