# ================================================================
# DOCKERFILE — Production Python FastAPI (PostgreSQL + Redis)
# ================================================================
#
# Multi-stage build:
#   builder   — installs all dependencies (incl. build tools)
#   runtime   — minimal image with non-root user, only what's needed
#
# Usage:
#   docker build -t app:latest .
#   docker run -d -p 8000:8000 app:latest
#
# Required env vars at runtime:
#   DATABASE_URL   postgresql+asyncpg://user:pass@host/db
#   REDIS_URL      redis://host:6379/0
# ================================================================

# ── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ──
# STAGE 1 — Builder
# ── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ──
FROM python:3.12-slim-bookworm AS builder

# Prevent Python from writing .pyc / buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System build deps — psycopg2 needs libpq-dev,
# and we need gcc for binary wheels of hiredis / uvloop / orjson
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtualenv inside the build stage
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Layer caching optimisation: copy & install requirements FIRST
# so Docker caches this layer separately from the app source code.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ──
# STAGE 2 — Runtime
# ── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ──
FROM python:3.12-slim-bookworm AS runtime

# ── Capabilities & users ────────────────────────────────────
# Drop root — create a non-privileged app user (no shell, no
# login).  Group 1000, user 1000.
RUN groupadd --gid 1000 --system app \
    && useradd --uid 1000 --gid 1000 --no-create-home --system app

# ── Runtime system deps ─────────────────────────────────────
# Only the shared libraries needed by the compiled extensions
# (libpq5 for asyncpg/psycopg2, libc for everything else).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Environment ─────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    APP_HOME=/app

# ── Copy virtualenv from builder (keeps runtime small) ──────
COPY --from=builder /venv /venv

# ── Application code ────────────────────────────────────────
WORKDIR $APP_HOME
COPY --chown=app:app . .

# ── Healthcheck ─────────────────────────────────────────────
# Uses the app's own /health endpoint via Uvicorn's internal
# HTTP client.  Interval every 30 s, timeout 10 s, 3 retries
# before marking unhealthy.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# ── Run as non-root user ────────────────────────────────────
USER app:app

# ── Expose port ─────────────────────────────────────────────
EXPOSE 8000

# ── Entrypoint ──────────────────────────────────────────────
# Exec-form so the process receives SIGTERM directly (no shell
# wrapper).  Uvicorn translates SIGTERM into a graceful
# shutdown — drains in-flight requests, closes connections.
#
# --forwarded-allow-ips  keeps trusted-proxy headers working
# --proxy-headers        reads X-Forwarded-* when behind a
#                        reverse proxy (nginx, Caddy, Traefik)
# --timeout-graceful-shutdown  30 s drain period
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--forwarded-allow-ips", "*", \
     "--proxy-headers", \
     "--timeout-graceful-shutdown", "30"]
