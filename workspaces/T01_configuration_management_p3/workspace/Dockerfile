# =============================================================================
# Dockerfile — Python FastAPI Web App (PostgreSQL + Redis)
# Multi-stage build: builder → runtime
# =============================================================================
# Stage 1 — Builder: install dependencies with full toolchain
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# ---- Layer caching: copy only requirements first ----
# This layer is cached as long as requirements files don't change
COPY requirements.txt .
COPY requirements-dev.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-warn-script-location \
        --requirement requirements.txt

# Install production-only extras if available
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ -f requirements-prod.txt ]; then \
        pip install --user --no-warn-script-location \
            --requirement requirements-prod.txt; \
    fi


# =============================================================================
# Stage 2 — Runtime: minimal image with non-root user
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# System-level runtime dependencies (psycopg needs libpq, Redis clients are pure Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python runtime config
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Create non-root user with explicit UID/GID for security & consistency
RUN groupadd -r appuser -g 1001 && \
    useradd -r -g appuser -u 1001 -d /home/appuser -s /sbin/nologin appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Copy installed packages from builder (preserves permissions)
COPY --from=builder /root/.local /home/appuser/.local

WORKDIR /app

# Copy application code last (changes most frequently → invalidates cache last)
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# ── Healthcheck ──
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# ── Expose application port ──
EXPOSE 8000

# ── Signal handling & process management ──
# exec-form CMD ensures uvicorn receives SIGTERM directly (PID 1).
# Graceful shutdown: uvicorn catches SIGTERM, drains in-flight requests,
# then exits cleanly — no orphaned database connections.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--timeout-graceful-shutdown", "30", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
