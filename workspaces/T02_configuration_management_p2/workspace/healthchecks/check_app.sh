#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Health check for the FastAPI application
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

URL="${1:-http://localhost:8000/health}"
TIMEOUT=5

response=$(curl -sf --max-time "$TIMEOUT" "$URL" 2>/dev/null || true)

if echo "$response" | grep -q '"status":"healthy"'; then
    exit 0
else
    echo "Health check failed for $URL"
    exit 1
fi
