#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Health check for PostgreSQL
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

USER="${POSTGRES_USER:-app_user}"
DB="${POSTGRES_DB:-fastapi_app}"

pg_isready -U "$USER" -d "$DB" -q
