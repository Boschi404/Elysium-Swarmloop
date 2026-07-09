# Elysium Swarmloop
The Self-Improving Multi-Agent Orchestration Engine

*Towards Agentic Utopia.*

## What is Elysium Swarmloop?

A Hermes Agent skill (SKILL.md) that transforms every prompt into an autonomous agentic workflow:

- **Massive parallelism** — up to 100 subagents per batch
- **Hierarchical orchestration** — depth-2: orchestrators spawn leaf workers
- **Streaming quality gate** — retry failures immediately, don't wait for batch completion
- **Self-learning** — captures patterns, calibrates granularity, improves iteration after iteration
- **Zero human intervention** — the loop keeps going until the goal is achieved

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

1. Add this SKILL.md to your Hermes Agent skills directory
2. Set `max_concurrent_children` and `max_spawn_depth: 2` in config.yaml
3. Every prompt from then on runs through the autonomous loop

## Versioning

This skill is self-improving. Each meaningful improvement bumps the version:

- **Patch (v5.1)** — new pitfall or calibration tweak
- **Minor (v5.5)** — new pattern or phase
- **Major (v6.0)** — breakthrough architecture change

## License

MIT
