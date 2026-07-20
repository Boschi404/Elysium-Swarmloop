# =============================================================================
# Stage 1 — Builder: install dependencies
# =============================================================================
FROM python:3.11-slim AS builder

# ═════════════════════════════════════════════════════════════════════════════
# Layer-caching optimisation — system deps (infrequent changes)
# ═════════════════════════════════════════════════════════════════════════════
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ═════════════════════════════════════════════════════════════════════════════
# Layer-caching optimisation — pip / uv first (infrequent changes)
# ═════════════════════════════════════════════════════════════════════════════
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --upgrade pip wheel setuptools

# ═════════════════════════════════════════════════════════════════════════════
# Layer-caching optimisation — dependencies (change with requirements.txt)
# ═════════════════════════════════════════════════════════════════════════════
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ═════════════════════════════════════════════════════════════════════════════
# Application source (changes most frequently — last layer)
# ═════════════════════════════════════════════════════════════════════════════
COPY app/ ./app/

# ═════════════════════════════════════════════════════════════════════════════
# Pre-compile Python bytecode so runtime container doesn't waste CPU on it
# ═════════════════════════════════════════════════════════════════════════════
RUN python -m compileall -q app/


# =============================================================================
# Stage 2 — Runtime: smallest possible production image
# =============================================================================
FROM python:3.11-slim AS runtime

# ─────────────────────────────────────────────────────────────────────────────
# 1. Runtime system deps (libpq for psycopg2, redis tools for healthcheck)
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    redis-tools \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
# 2. Non-root user (security best-practice)
# ─────────────────────────────────────────────────────────────────────────────
RUN groupadd -r fastapi && useradd -r -g fastapi -d /app -s /sbin/nologin fastapi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Copy dependencies & app from builder (keeps runtime layer small)
# ─────────────────────────────────────────────────────────────────────────────
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/ /app/

# ─────────────────────────────────────────────────────────────────────────────
# 4. Runtime directory & ownership
# ─────────────────────────────────────────────────────────────────────────────
RUN mkdir -p /app && chown -R fastapi:fastapi /app

WORKDIR /app
USER fastapi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Application metadata
# ─────────────────────────────────────────────────────────────────────────────
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_MODULE=app.main:app \
    MAX_WORKERS=4

# ─────────────────────────────────────────────────────────────────────────────
# 6. Healthcheck — uses ping endpoint from the FastAPI app
# ─────────────────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5).read()"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Proper signal handling — exec-form ENTRYPOINT + CMD so PID 1 is the
#    Python process and receives SIGTERM/SIGINT directly (no shell wrapping)
# ─────────────────────────────────────────────────────────────────────────────
ENTRYPOINT ["python"]
CMD ["-m", "gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--forwarded-allow-ips", "*", \
     "--log-level", "info"]
