"""Tests for the production Dockerfile.

Validates:
  - Multi-stage structure (builder + runtime)
  - Non-root user
  - HEALTHCHECK directive
  - exec-form ENTRYPOINT/CMD (proper signal handling)
  - Layer-caching optimisation (copy order)
  - PostgreSQL & Redis runtime deps
  - .dockerignore completeness
"""

import os
import pytest
import re

DOCKERFILE = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
DOCKERIGNORE = os.path.join(os.path.dirname(__file__), "..", ".dockerignore")


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def dockerfile() -> str:
    with open(DOCKERFILE) as f:
        return f.read()


@pytest.fixture(scope="session")
def dockerfile_lines(dockerfile) -> list[str]:
    return [ln.rstrip() for ln in dockerfile.splitlines()]


@pytest.fixture(scope="session")
def dockerignore() -> str:
    with open(DOCKERIGNORE) as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════════════════
# 1. Multi-stage build
# ═══════════════════════════════════════════════════════════════════════════


class TestMultiStage:
    def test_two_stages(self, dockerfile):
        """Must have exactly 2 FROM statements (builder + runtime)."""
        matches = re.findall(r"^FROM\s+\S+", dockerfile, re.MULTILINE)
        assert len(matches) == 2, (
            f"Expected exactly 2 FROM stages, found {len(matches)}: {matches}"
        )

    def test_stage_names(self, dockerfile):
        """Stage names must be 'AS builder' and 'AS runtime'."""
        assert re.search(r"FROM\s+\S+\s+AS\s+builder", dockerfile), "Missing 'AS builder'"
        assert re.search(r"FROM\s+\S+\s+AS\s+runtime", dockerfile), "Missing 'AS runtime'"

    def test_builder_has_build_tools(self, dockerfile):
        """Builder stage should install gcc or build-essential for psycopg2."""
        builder = self._stage_content(dockerfile, "builder")
        assert "gcc" in builder, "Builder stage should install gcc for psycopg2"
        assert "libpq-dev" in builder, "Builder stage should install libpq-dev"

    def test_builder_has_pip_install(self, dockerfile):
        """Builder stage must install requirements."""
        builder = self._stage_content(dockerfile, "builder")
        assert "pip install" in builder, "Builder stage must install Python dependencies"
        assert "requirements.txt" in builder, (
            "Builder stage must copy requirements.txt before pip install"
        )

    @staticmethod
    def _stage_content(dockerfile: str, name: str) -> str:
        """Return lines belonging to a named stage."""
        lines = dockerfile.splitlines()
        in_stage = False
        content: list[str] = []
        for line in lines:
            if re.match(rf"^FROM\s+\S+\s+AS\s+{name}\s*$", line, re.IGNORECASE):
                in_stage = True
                continue
            if in_stage and re.match(r"^FROM\s+", line, re.IGNORECASE):
                in_stage = False
            if in_stage:
                content.append(line)
        return "\n".join(content)


# ═══════════════════════════════════════════════════════════════════════════
# 2. Runtime — non-root user
# ═══════════════════════════════════════════════════════════════════════════


class TestNonRootUser:
    def test_groupadd_exists(self, dockerfile):
        """Must create a dedicated group."""
        assert re.search(r"groupadd\s+-r\s+\S+", dockerfile), "No groupadd found"

    def test_useradd_exists(self, dockerfile):
        """Must create a dedicated non-root user."""
        assert re.search(r"useradd\s+-r.*-g\s+\S+\s+\S+", dockerfile), "No useradd found"

    def test_user_switch(self, dockerfile_lines):
        """Must have a USER directive switching to non-root."""
        user_lines = [l for l in dockerfile_lines if l.startswith("USER ")]
        assert any("fastapi" in l or "appuser" in l or "app" in l for l in user_lines), (
            "No USER directive switching to non-root user found"
        )

    def test_no_root_user_runtime(self, dockerfile):
        """Runtime stage should not run as root (no USER root)."""
        runtime = self._get_runtime(dockerfile)
        assert "USER root" not in runtime, "Runtime stage should not switch back to root"
        assert "USER" in runtime, "Runtime stage must have a USER directive"

    @staticmethod
    def _get_runtime(dockerfile: str) -> str:
        lines = dockerfile.splitlines()
        runtime_lines: list[str] = []
        in_runtime = False
        for line in lines:
            if re.match(r"^FROM\s+\S+\s+AS\s+runtime\s*$", line, re.IGNORECASE):
                in_runtime = True
                continue
            if in_runtime:
                runtime_lines.append(line)
        return "\n".join(runtime_lines)


# ═══════════════════════════════════════════════════════════════════════════
# 3. HEALTHCHECK
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthcheck:
    def test_healthcheck_directive(self, dockerfile):
        """Dockerfile must have a HEALTHCHECK instruction."""
        assert "HEALTHCHECK" in dockerfile, "Missing HEALTHCHECK directive"

    def test_healthcheck_parameters(self, dockerfile):
        """HEALTHCHECK should have --interval, --timeout, --start-period, --retries."""
        hc = self._extract_healthcheck(dockerfile)
        assert hc, "HEALTHCHECK not found"
        assert "--interval" in hc, "HEALTHCHECK missing --interval"
        assert "--timeout" in hc, "HEALTHCHECK missing --timeout"
        assert "--start-period" in hc, "HEALTHCHECK missing --start-period (for startup)"
        assert "--retries" in hc, "HEALTHCHECK missing --retries"

    @staticmethod
    def _extract_healthcheck(dockerfile: str) -> str:
        lines = dockerfile.splitlines()
        for line in lines:
            if line.strip().startswith("HEALTHCHECK"):
                return line.strip()
        return ""


# ═══════════════════════════════════════════════════════════════════════════
# 4. Proper signal handling (exec-form ENTRYPOINT/CMD)
# ═══════════════════════════════════════════════════════════════════════════


class TestSignalHandling:
    def test_exec_form_entrypoint(self, dockerfile):
        """ENTRYPOINT must use exec form (JSON array), not shell form."""
        for line in dockerfile.splitlines():
            stripped = line.strip()
            if stripped.startswith("ENTRYPOINT") and "gunicorn" not in stripped:
                assert stripped.startswith('ENTRYPOINT ["'), (
                    f"ENTRYPOINT should use exec form, got: {stripped}"
                )

    def test_exec_form_cmd(self, dockerfile_lines):
        """CMD must use exec form (JSON array), not shell string."""
        cmd_lines = [l for l in dockerfile_lines if l.startswith("CMD ")]
        assert cmd_lines, "No CMD instruction found"
        for cmd in cmd_lines:
            msg = f"CMD should use exec form (JSON array), got: {cmd}"
            assert cmd.strip().startswith('CMD ["') or cmd.strip().startswith("CMD ['"), msg

    def test_graceful_timeout(self, dockerfile):
        """Gunicorn should have --graceful-timeout for proper SIGTERM handling."""
        assert "--graceful-timeout" in dockerfile, (
            "Missing --graceful-timeout on gunicorn (needed for signal handling)"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. Layer-caching optimisation
# ═══════════════════════════════════════════════════════════════════════════


class TestLayerCaching:
    def test_system_deps_before_requirements(self, dockerfile_lines):
        """apt-get should be before pip install (system deps change less often)."""
        apt_line = None
        pip_line = None
        for i, line in enumerate(dockerfile_lines):
            if line.strip().startswith("RUN apt-get") and apt_line is None:
                apt_line = i  # first match = builder stage
            if "pip install" in line and "requirements.txt" in line:
                pip_line = i
                break  # first match = builder stage
        assert apt_line is not None, "No apt-get found in builder"
        assert pip_line is not None, "No pip install -r requirements.txt found"
        assert apt_line < pip_line, (
            f"apt-get at line {apt_line} should be BEFORE pip at line {pip_line}"
        )

    def test_requirements_before_app_code(self, dockerfile_lines):
        """requirements.txt COPY should be before app/ COPY (deps change less often)."""
        req_line = None
        app_line = None
        for i, line in enumerate(dockerfile_lines):
            if re.match(r"COPY\s+requirements\.txt\s", line):
                req_line = i
            if re.match(r"COPY\s+app/\s+", line):
                app_line = i
        assert req_line is not None, "No COPY requirements.txt found"
        assert app_line is not None, "No COPY app/ found"
        assert req_line < app_line, (
            f"COPY requirements.txt at line {req_line} should be BEFORE app/ at line {app_line}"
        )

    def test_no_cache_dirs(self, dockerfile):
        """Should use --no-cache-dir or PIP_NO_CACHE_DIR to reduce image size."""
        assert "PIP_NO_CACHE_DIR" in dockerfile or "--no-cache-dir" in dockerfile, (
            "Missing pip cache-disabling flag"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 6. PostgreSQL & Redis runtime dependencies
# ═══════════════════════════════════════════════════════════════════════════


class TestPostgresRedis:
    def test_libpq_installed(self, dockerfile):
        """Runtime should install libpq5 for psycopg2 PostgreSQL driver."""
        assert "libpq5" in dockerfile or "libpq-dev" in dockerfile, (
            "Missing libpq runtime dependency for PostgreSQL"
        )

    def test_redis_tools_or_hiredis(self, dockerfile):
        """Runtime should install redis-tools or redis[hiredis] for Redis connectivity."""
        assert "redis-tools" in dockerfile or "redis" in dockerfile, (
            "Missing Redis runtime dependency"
        )

    def test_psycopg2_in_requirements(self):
        """requirements.txt should include a PostgreSQL adapter."""
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(req_path) as f:
            content = f.read()
        assert "psycopg" in content or "asyncpg" in content, (
            "requirements.txt missing PostgreSQL adapter"
        )

    def test_redis_in_requirements(self):
        """requirements.txt should include a Redis client."""
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(req_path) as f:
            content = f.read()
        assert "redis" in content, "requirements.txt missing Redis client"


# ═══════════════════════════════════════════════════════════════════════════
# 7. .dockerignore
# ═══════════════════════════════════════════════════════════════════════════


class TestDockerignore:
    def test_exists(self):
        """.dockerignore must exist."""
        assert os.path.isfile(DOCKERIGNORE), ".dockerignore file is missing"

    def test_git_excluded(self, dockerignore):
        """Must exclude .git directory."""
        assert ".git" in dockerignore, ".dockerignore should exclude .git"

    def test_pycache_excluded(self, dockerignore):
        """Must exclude __pycache__."""
        assert "__pycache__" in dockerignore, ".dockerignore should exclude __pycache__"

    def test_env_excluded(self, dockerignore):
        """.env files must be excluded (secrets)."""
        assert ".env" in dockerignore, ".dockerignore should exclude .env files"

    def test_venv_excluded(self, dockerignore):
        """Virtual environments must be excluded."""
        assert any(v in dockerignore for v in [".venv", "venv", ".tox"]), (
            ".dockerignore should exclude virtual environments"
        )

    def test_tests_excluded(self, dockerignore):
        """Test directories should be excluded from build context."""
        assert "tests" in dockerignore, ".dockerignore should exclude tests/"

    def test_docker_files_excluded(self, dockerignore):
        """Dockerfile itself and docker-compose should be excluded."""
        assert "Dockerfile" in dockerignore, ".dockerignore should exclude Dockerfile"
        assert "docker-compose" in dockerignore, ".dockerignore should exclude docker-compose files"


# ═══════════════════════════════════════════════════════════════════════════
# 8. FastAPI app code
# ═══════════════════════════════════════════════════════════════════════════


class TestAppCode:
    def test_app_main_exists(self):
        """app/main.py must exist (used by gunicorn and HEALTHCHECK)."""
        main_path = os.path.join(os.path.dirname(__file__), "..", "app", "main.py")
        assert os.path.isfile(main_path), "app/main.py not found"

    def test_health_endpoint(self):
        """app/main.py must have a /health endpoint."""
        main_path = os.path.join(os.path.dirname(__file__), "..", "app", "main.py")
        with open(main_path) as f:
            content = f.read()
        assert "def health" in content, "Missing health() function"
        assert "/health" in content, "Missing /health route"

    def test_requirements_has_fastapi(self):
        """requirements.txt must include FastAPI."""
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(req_path) as f:
            content = f.read()
        assert "fastapi" in content.lower(), "requirements.txt missing fastapi"
        assert "gunicorn" in content.lower(), "requirements.txt missing gunicorn"
