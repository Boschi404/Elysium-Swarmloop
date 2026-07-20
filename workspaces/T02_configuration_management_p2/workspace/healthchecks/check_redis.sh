#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Health check for Redis
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PASSWORD="${REDIS_PASSWORD:-}"

if [ -n "$PASSWORD" ]; then
    redis-cli -a "$PASSWORD" ping 2>/dev/null | grep -q PONG
else
    redis-cli ping 2>/dev/null | grep -q PONG
fi
