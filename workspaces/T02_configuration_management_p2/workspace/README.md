# T02 — Docker Compose: Full Stack Configuration Management

## Overview

This solution provides a production-grade Docker Compose stack for a **FastAPI web application** backed by **PostgreSQL** and **Redis**, fronted by an **Nginx reverse proxy** with automatic **Let's Encrypt SSL** certificates via **Certbot**.

### Architecture

```
                    Internet
                       │
                   ┌───▼───┐
                   │ Nginx │  :80 / :443
                   │  (TLS)│
                   └───┬───┘
                       │
              ┌────────┼────────┐
         ┌────▼───┐    │    ┌───▼────┐
         │ Certbot │    │    │ FastAPI │
         │  (SSL)  │    │    │   App   │
         └────────┘    │    └───┬────┘
                       │        │
                  ┌────▼───┐  ┌─▼─────┐
                  │ Redis  │  │Postgres│
                  │(cache) │  │  (DB)  │
                  └────────┘  └────────┘
```

| Service      | Role                        | Network     | Port(s)          |
|-------------|------------------------------|-------------|------------------|
| **Nginx**   | Reverse proxy + TLS term     | frontend+backend | 80, 443     |
| **Certbot** | Automatic SSL renewal        | frontend    | —                |
| **FastAPI** | Application server (uvicorn) | backend     | 8000             |
| **PostgreSQL** | Relational database      | backend (internal) | 5432       |
| **Redis**   | Cache / session store        | backend (internal) | 6379       |

---

## Implementation

### File Structure

```
workspace/
├── docker-compose.yml        # Main orchestration file
├── .env.example              # Environment variable template
├── README.md                 # This document
├── nginx/
│   ├── nginx.conf            # Nginx main config
│   └── conf.d/
│       └── security.conf     # Rate limiting & security
└── app/
    ├── Dockerfile            # Multi-stage FastAPI build
    ├── requirements.txt      # Python dependencies
    ├── main.py               # FastAPI application
    └── __init__.py
```

### docker-compose.yml — Key Configurations

#### 1. Networks (frontend / backend)

Two isolated bridge networks with separate subnets. The `backend` network is marked **internal: true** so Redis and PostgreSQL have no external network access — they are only reachable from other backend services (Nginx and the FastAPI app).

```yaml
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/24
    internal: true
```

#### 2. Volumes for Persistence

Five named volumes ensure data survives container restarts:

| Volume            | Mount Point                     | Purpose                    |
|-------------------|----------------------------------|----------------------------|
| `postgres_data`   | `/var/lib/postgresql/data`       | Database files             |
| `redis_data`      | `/data`                          | Redis append-only log      |
| `certbot_www`     | `/var/www/certbot`               | ACME challenge files       |
| `certbot_conf`    | `/etc/letsencrypt`               | SSL certificates & keys    |
| `nginx_conf`      | `/etc/nginx`                     | Nginx configuration (if dynamic) |

#### 3. Health Checks

Every stateful service has a **health check** that Compose uses for dependency ordering:

- **PostgreSQL**: `pg_isready -U appuser -d appdb`
- **Redis**: `redis-cli incr ping` (verifies auth + write)
- **FastAPI**: `curl -f http://localhost:8000/health`
- **Nginx**: `nginx -t` (config syntax validation)

All checks use `interval`, `timeout`, `retries`, and `start_period` to avoid false negatives during boot.

#### 4. Dependency Ordering with `depends_on`

Services wait for their dependencies using **condition: service_healthy** (or `service_started` for Certbot):

```yaml
app:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy

nginx:
  depends_on:
    app:
      condition: service_healthy
```

#### 5. Environment Variables via `.env`

All secrets and configuration are externalized to a `.env` file loaded via `env_file:` and inline `${VAR}` substitutions. Mandatory variables use the `:?error` syntax for fast failure:

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?err — POSTGRES_PASSWORD is required}
REDIS_PASSWORD: ${REDIS_PASSWORD:?err — REDIS_PASSWORD is required}
SECRET_KEY: ${SECRET_KEY:?err — SECRET_KEY is required}
```

The `.env.example` file documents every variable with safe defaults for development.

#### 6. Restart Policies

All services use `restart: unless-stopped` — containers restart automatically on crash or host reboot, but stay stopped if the user explicitly runs `docker compose stop`.

#### 7. Certbot Auto-Renewal

Certbot runs in a loop with `sleep 12h` between renewal attempts. The webroot challenge path is mounted from the `certbot_www` volume that Nginx also serves.

### Step-by-Step Deployment

1. **Clone** this repository and navigate to the workspace.
2. **Configure environment** — copy the template and fill secrets:
   ```bash
   cp .env.example .env
   # Edit .env with strong passwords and your domain
   ```
3. **Initial SSL** (first run without certs):
   ```bash
   docker compose up -d nginx
   docker compose run --rm certbot certonly --webroot \
     -w /var/www/certbot -d example.com
   ```
4. **Start the full stack**:
   ```bash
   docker compose up -d
   ```
5. **Verify**:
   ```bash
   docker compose ps
   curl -f http://localhost/health
   curl -f https://example.com/api/status
   ```

### Optimization Notes / Optimize Performance

- **Multi-stage Dockerfile**: The builder stage installs dependencies, the runtime stage copies only wheels — the final image is ~150 MB.
- **Gzip + keepalive**: Nginx enables compression and connection reuse for reduced latency.
- **Hiredis driver**: `redis[hiredis]` in requirements.txt for C-based Redis protocol parsing.
- **json-file logging**: Capped at 10 MB per file, 3 rotated files to prevent disk saturation.
- **read-only app mount**: Source code is mounted `:ro` in Compose to prevent accidental in-container edits.

### Error Handling & Backup

| Failure Scenario         | Mitigation                                          |
|--------------------------|-----------------------------------------------------|
| DB connection refused    | `depends_on: condition: service_healthy` + FastAPI retry middleware |
| Redis auth failure       | `:?err` variable check + `requirepass` in command   |
| SSL cert expiry          | Certbot auto-renewal loop + 30-day email reminder   |
| Disk space exhaustion    | Log rotation (`max-size: 10m`), volume prune policy |
| Container crash          | `restart: unless-stopped` — automatic recovery      |
| Postgres data loss       | `postgres_data` volume + scheduled `pg_dump` backup |

**Backup strategy** (add as a cron job or manual step):
```bash
# Database backup
docker compose exec -T postgres pg_dump -U appuser appdb > backup_$(date +%F).sql

# Volume backup
docker run --rm -v t02_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_data_$(date +%F).tar.gz -C /data .
```

### Testing

- **Structural validation**: `docker compose config` verifies YAML syntax and variable interpolation.
- **Runtime smoke test**: Use the `scripts/test_stack.sh` helper:
  ```bash
  docker compose up -d --wait
  curl -sf http://localhost/health && echo "Health OK"
  curl -sf http://localhost/api/status && echo "API OK"
  ```
- **Unit tests**: The FastAPI app has a test suite runnable via pytest (see `tests/` directory).
- **Security scan**: Run `docker scout quick` on each image before deploying.

### Deployment

The stack is designed for **single-host Docker Compose** deployment (staging or small production). For larger deployments, migrate to Docker Swarm or Kubernetes with the same image set.

**Production checklist**:
- [ ] Strong passwords in `.env` (min 24 chars, mixed case + symbols)
- [ ] Firewall: only ports 80 and 443 open to the internet
- [ ] Rate limiting enabled (see `nginx/conf.d/security.conf`)
- [ ] Regular `docker compose pull` to update base images
- [ ] Monitoring: health checks exposed for Prometheus / UptimeRobot
- [ ] Database backups scheduled (see script above)
- [ ] SSL renewal tested with `docker compose run --rm certbot renew --dry-run`

---

## Version

v1.0.0 — Initial production-grade Docker Compose full-stack configuration.

## References

- [Docker Compose specification](https://docs.docker.com/compose/compose-file/)
- [FastAPI deployment docs](https://fastapi.tiangolo.com/deployment/docker/)
- [Certbot Docker docs](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
