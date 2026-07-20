# ──────────────────────────────────────────────────────────────────────────────
# Stage 1 — Python dependencies (cached layer)
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime image
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# System dependencies for asyncpg / psycopg2, health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libpq-dev \
        gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Application code
COPY app/ ./app/
COPY .env .

# Non-root user for security
RUN groupadd -r fastapi && useradd -r -g fastapi -d /app fastapi
RUN chown -R fastapi:fastapi /app

EXPOSE 8000

USER fastapi

# Run with uvicorn — Gunicorn is not needed for production when behind Nginx
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]
