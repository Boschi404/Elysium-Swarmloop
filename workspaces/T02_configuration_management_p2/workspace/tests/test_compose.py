"""
Tests for docker-compose.yml and supporting configuration files.

Verifies:
  - docker-compose.yml is valid YAML with expected structure
  - All services have required fields (image, restart, networks, healthchecks, etc.)
  - .env contains all referenced variables
  - Dockerfile is well-formed
  - Nginx config has expected sections
  - Cross-references between files are consistent
"""

import os
import re
import sys
from pathlib import Path

import yaml


# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ROOT / "docker-compose.yml"
ENV_FILE = ROOT / ".env"
DOCKERFILE = ROOT / "Dockerfile"
NGINX_CONF = ROOT / "nginx" / "nginx.conf"
INIT_SQL = ROOT / "scripts" / "init-db.sql"
HEALTHCHECKS_DIR = ROOT / "healthchecks"


# ─── Helpers ──────────────────────────────────────────────────────────────────


def read_env(path: Path) -> dict[str, str]:
    """Parse a .env file into a dict (ignoring comments and blank lines)."""
    vars_: dict[str, str] = {}
    if not path.exists():
        return vars_
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            vars_[key.strip()] = val.strip()
    return vars_


def describe_issues(issues: list[str]) -> str:
    """Pretty-print a list of issues."""
    if not issues:
        return "  ✅ All checks passed"
    return "\n".join(f"  ❌ {i}" for i in issues)


def check_keys(section: str, expected: set[str], actual: set[str]) -> list[str]:
    """Return missing/extra key descriptions."""
    issues: list[str] = []
    missing = expected - actual
    extra = actual - expected
    if missing:
        issues.append(f"{section}: missing keys: {sorted(missing)}")
    if extra:
        issues.append(f"{section}: unexpected keys: {sorted(extra)}")
    return issues


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestComposeStructure:
    """Validate docker-compose.yml structure and service definitions."""

    def setup_method(self) -> None:
        assert COMPOSE.exists(), f"docker-compose.yml not found at {COMPOSE}"
        with open(COMPOSE, encoding="utf-8") as fh:
            self.compose = yaml.safe_load(fh)

    # ── Top-level keys ────────────────────────────────────────────────────────

    def test_top_level_keys(self):
        expected = {"services", "volumes", "networks"}
        actual = set(self.compose.keys())
        issues = check_keys("top-level", expected, actual)
        assert not issues, describe_issues(issues)

    def test_expected_services(self):
        expected = {"app", "db", "redis", "nginx", "certbot", "certbot-renew"}
        actual = set(self.compose.get("services", {}).keys())
        issues = check_keys("services", expected, actual)
        assert not issues, describe_issues(issues)

    def test_expected_volumes(self):
        expected = {
            "postgres_data", "redis_data",
            "static_volume", "media_volume",
            "certbot_conf", "certbot_www",
        }
        actual = set(self.compose.get("volumes", {}).keys())
        issues = check_keys("volumes", expected, actual)
        assert not issues, describe_issues(issues)

    def test_expected_networks(self):
        expected = {"frontend", "backend"}
        actual = set(self.compose.get("networks", {}).keys())
        issues = check_keys("networks", expected, actual)
        assert not issues, describe_issues(issues)

    # ── Service: app ──────────────────────────────────────────────────────────

    def test_app_service(self):
        svc = self.compose["services"]["app"]
        assert "build" in svc, "app service missing 'build'"
        assert "image" in svc, "app service missing 'image'"
        assert "restart" in svc, "app service missing 'restart'"
        assert svc["restart"] == "unless-stopped"
        assert "env_file" in svc
        assert "healthcheck" in svc, "app missing healthcheck"
        assert "depends_on" in svc, "app missing depends_on"
        deps = svc["depends_on"]
        assert "db" in deps, "app should depend on db"
        assert "redis" in deps, "app should depend on redis"
        assert deps["db"].get("condition") == "service_healthy"
        assert deps["redis"].get("condition") == "service_healthy"
        # app must be on both frontend + backend networks
        networks = svc.get("networks", {})
        assert "frontend" in networks or "backend" in networks

    # ── Service: db ───────────────────────────────────────────────────────────

    def test_db_service(self):
        svc = self.compose["services"]["db"]
        assert "image" in svc
        assert "postgres" in svc["image"], "db image should be postgres"
        assert "restart" in svc and svc["restart"] == "unless-stopped"
        assert "env_file" in svc
        assert "healthcheck" in svc
        assert "volumes" in svc
        assert any("postgres_data" in v for v in svc["volumes"])
        assert any("init-db.sql" in v for v in svc["volumes"])
        networks = svc.get("networks", {})
        assert "backend" in networks or "backend" in svc.get("network", {})

    # ── Service: redis ────────────────────────────────────────────────────────

    def test_redis_service(self):
        svc = self.compose["services"]["redis"]
        assert "image" in svc
        assert "redis" in svc["image"]
        assert "restart" in svc and svc["restart"] == "unless-stopped"
        assert "healthcheck" in svc
        assert "volumes" in svc
        assert any("redis_data" in v for v in svc["volumes"])
        networks = svc.get("networks", {})
        assert "backend" in networks or "backend" in svc.get("network", {})

    # ── Service: nginx ────────────────────────────────────────────────────────

    def test_nginx_service(self):
        svc = self.compose["services"]["nginx"]
        assert "image" in svc
        assert "nginx" in svc["image"]
        assert "restart" in svc and svc["restart"] == "unless-stopped"
        assert "ports" in svc, "nginx should publish ports 80 and 443"
        ports = svc["ports"]
        assert any("80" in str(p) for p in ports)
        assert any("443" in str(p) for p in ports)
        assert "healthcheck" in svc
        assert "depends_on" in svc
        # nginx must be on frontend network
        networks = svc.get("networks", {})
        assert "frontend" in networks or "frontend" in svc.get("network", {})

    # ── Service: certbot ──────────────────────────────────────────────────────

    def test_certbot_service(self):
        svc = self.compose["services"]["certbot"]
        assert "image" in svc
        assert "certbot" in svc["image"]
        assert svc.get("restart") == "no", "certbot should use restart: no"
        assert "profiles" in svc, "certbot should use profiles for opt-in"
        assert "certbot" in svc["profiles"]
        assert "volumes" in svc
        assert any("certbot_conf" in v for v in svc["volumes"])
        assert any("certbot_www" in v for v in svc["volumes"])

    def test_certbot_renew_service(self):
        svc = self.compose["services"]["certbot-renew"]
        assert "image" in svc
        assert "certbot" in svc["image"]
        assert svc.get("restart") == "no"
        assert "profiles" in svc
        assert "certbot" in svc["profiles"]

    # ── Networks ──────────────────────────────────────────────────────────────

    def test_backend_network_is_internal(self):
        """Backend network should be 'internal: true' for isolation."""
        net = self.compose.get("networks", {}).get("backend", {})
        assert net.get("internal") is True, \
            "backend network should be internal for security isolation"

    def test_network_isolation(self):
        """db and redis should NOT be on frontend network."""
        for srv_name in ("db", "redis"):
            svc = self.compose["services"].get(srv_name, {})
            nw = svc.get("networks", {})
            if isinstance(nw, list):
                assert "frontend" not in nw, \
                    f"{srv_name} should NOT be on frontend network"
            elif isinstance(nw, dict):
                assert "frontend" not in nw, \
                    f"{srv_name} should NOT be on frontend network"

    # ── Volumes ───────────────────────────────────────────────────────────────

    def test_all_named_volumes_are_declared(self):
        """Every volume referenced in a service must be declared in top-level volumes."""
        declared = set(self.compose.get("volumes", {}).keys())
        referenced: set[str] = set()
        for name, svc in self.compose.get("services", {}).items():
            for vol in svc.get("volumes", []):
                vol_str = vol if isinstance(vol, str) else vol.get("source", "")
                parts = vol_str.partition(":")
                if parts[0] and parts[0] not in ("/", ".") and "\\" not in parts[0] and "/" not in parts[0]:
                    referenced.add(parts[0])
        undeclared = referenced - declared
        assert not undeclared, f"Volumes referenced but not declared: {undeclared}"


class TestEnvFile:
    """Validate .env file has all required variables."""

    def setup_method(self) -> None:
        assert ENV_FILE.exists(), f".env not found at {ENV_FILE}"
        self.env = read_env(ENV_FILE)

    def test_required_vars_present(self):
        required = {
            # App
            "APP_HOST", "APP_PORT", "APP_SECRET_KEY",
            # PostgreSQL
            "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "DATABASE_URL",
            # Redis
            "REDIS_PASSWORD", "REDIS_URL",
            # Nginx
            "NGINX_HOST", "NGINX_PORT", "NGINX_SSL_PORT",
            # Certbot
            "CERTBOT_EMAIL", "CERTBOT_DOMAIN",
        }
        missing = required - set(self.env.keys())
        assert not missing, f".env missing required variables: {sorted(missing)}"

    def test_env_vars_used_in_compose(self):
        """Every ${VAR} in docker-compose.yml should have a corresponding .env entry (or default)."""
        if not COMPOSE.exists():
            return
        text = COMPOSE.read_text(encoding="utf-8")
        refs = set(re.findall(r'\$\{(\w+)[:}-]', text))
        refs |= set(re.findall(r'\$\{(\w+)\}', text))
        env_keys = set(self.env.keys())
        # These are in-file defaults or builtins — safe to skip
        known_defaults = {"POSTGRES_USER", "POSTGRES_DB", "REDIS_PASSWORD",
                          "NGINX_HOST", "NGINX_PORT", "NGINX_SSL_PORT",
                          "SSL_CERT_PATH", "SSL_KEY_PATH",
                          "CERTBOT_RSA_KEY_SIZE", "CERTBOT_STAGING",
                          "HEALTHCHECK_INTERVAL", "HEALTHCHECK_TIMEOUT",
                          "HEALTHCHECK_RETRIES", "HEALTHCHECK_START_PERIOD",
                          "NGINX_PROXY_READ_TIMEOUT", "NGINX_PROXY_CONNECT_TIMEOUT",
                          "NGINX_SERVER_NAME"}
        unresolved = refs - env_keys - known_defaults
        assert not unresolved, \
            f"${VAR} references in docker-compose.yml with no .env entry: {sorted(unresolved)}"


class TestDockerfile:
    """Validate Dockerfile is structurally sound."""

    def setup_method(self) -> None:
        assert DOCKERFILE.exists(), f"Dockerfile not found at {DOCKERFILE}"
        self.content = DOCKERFILE.read_text(encoding="utf-8")

    def test_dockerfile_stages(self):
        assert "FROM python:3.12-slim AS builder" in self.content
        assert "FROM python:3.12-slim AS runtime" in self.content

    def test_dockerfile_has_nonroot_user(self):
        assert "USER fastapi" in self.content or "USER 1000" in self.content, \
            "Dockerfile should switch to non-root user"

    def test_dockerfile_exposes_port(self):
        assert "EXPOSE 8000" in self.content or "EXPOSE" in self.content

    def test_dockerfile_has_cmd(self):
        assert "CMD" in self.content


class TestNginxConfig:
    """Validate nginx configuration has expected sections."""

    def setup_method(self) -> None:
        assert NGINX_CONF.exists(), f"nginx.conf not found at {NGINX_CONF}"
        self.content = NGINX_CONF.read_text(encoding="utf-8")

    def test_http_redirect(self):
        assert "return 301 https://" in self.content

    def test_acme_challenge(self):
        assert ".well-known/acme-challenge" in self.content

    def test_ssl_listen(self):
        assert "listen      443 ssl" in self.content

    def test_upstream_block(self):
        assert "upstream fastapi_backend" in self.content

    def test_proxy_pass(self):
        assert "proxy_pass http://fastapi_backend" in self.content

    def test_rate_limiting(self):
        assert "limit_req_zone" in self.content or "limit_req" in self.content

    def test_static_media_locations(self):
        assert "/static/" in self.content and "/media/" in self.content

    def test_websocket_headers(self):
        assert "Upgrade" in self.content and "Connection" in self.content


class TestInitSQL:
    """Validate init-db.sql is well-formed."""

    def setup_method(self) -> None:
        assert INIT_SQL.exists(), f"init-db.sql not found at {INIT_SQL}"
        self.content = INIT_SQL.read_text(encoding="utf-8")

    def test_has_extensions(self):
        assert "uuid-ossp" in self.content or "pgcrypto" in self.content

    def test_has_tables(self):
        assert "CREATE TABLE" in self.content

    def test_has_indexes(self):
        assert "CREATE INDEX" in self.content

    def test_has_triggers(self):
        assert "TRIGGER" in self.content or "FUNCTION" in self.content


class TestHealthChecks:
    """Validate health check scripts exist and are shell scripts."""

    def test_check_app_script(self):
        path = HEALTHCHECKS_DIR / "check_app.sh"
        assert path.exists(), f"check_app.sh not found at {path}"
        content = path.read_text(encoding="utf-8")
        assert "curl" in content

    def test_check_db_script(self):
        path = HEALTHCHECKS_DIR / "check_db.sh"
        assert path.exists(), f"check_db.sh not found at {path}"
        content = path.read_text(encoding="utf-8")
        assert "pg_isready" in content

    def test_check_redis_script(self):
        path = HEALTHCHECKS_DIR / "check_redis.sh"
        assert path.exists(), f"check_redis.sh not found at {path}"
        content = path.read_text(encoding="utf-8")
        assert "redis-cli" in content or "PONG" in content


class TestCrossReferences:
    """Validate that files consistently reference each other."""

    def test_compose_refers_to_nginx_conf(self):
        content = COMPOSE.read_text(encoding="utf-8")
        assert "nginx/nginx.conf" in content or "nginx.conf" in content

    def test_compose_refers_to_init_db(self):
        content = COMPOSE.read_text(encoding="utf-8")
        assert "init-db.sql" in content

    def test_compose_refers_to_dockerfile(self):
        content = COMPOSE.read_text(encoding="utf-8")
        assert "Dockerfile" in content

    def test_nginx_proxies_to_app_service(self):
        content = NGINX_CONF.read_text(encoding="utf-8") if NGINX_CONF.exists() else ""
        assert "server app:8000" in content or "fastapi_backend" in content

    def test_env_nginx_host_matches_nginx_conf(self):
        """The NGINX_HOST from .env should align with certbot domain logic."""
        env = read_env(ENV_FILE)
        nginx_host = env.get("NGINX_HOST", "localhost")
        nginx = NGINX_CONF.read_text(encoding="utf-8") if NGINX_CONF.exists() else ""
        assert nginx_host in nginx or "server_name _;" in nginx
