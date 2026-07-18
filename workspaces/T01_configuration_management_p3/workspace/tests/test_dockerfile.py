"""Tests for Dockerfile and .dockerignore — validates structure & best practices."""

import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DOCKERFILE = WORKSPACE / "Dockerfile"
DOCKERIGNORE = WORKSPACE / ".dockerignore"


# ── Dockerfile presence ──

def test_dockerfile_exists():
    assert DOCKERFILE.is_file(), "Dockerfile not found"


def test_dockerignore_exists():
    assert DOCKERIGNORE.is_file(), ".dockerignore not found"


# ── Multi-stage structure ──

def test_multi_stage_build():
    content = DOCKERFILE.read_text()
    stages = re.findall(r"^FROM\s+\S+\s+AS\s+(\w+)", content, re.M | re.I)
    assert len(stages) >= 2, f"Expected ≥2 stages, got {stages}"


def test_named_builder_stage():
    content = DOCKERFILE.read_text()
    assert "AS builder" in content, "No 'builder' stage found"
    assert "AS runtime" in content or "AS final" in content, "No runtime stage found"


# ── Non-root user ──

def test_non_root_user():
    content = DOCKERFILE.read_text()
    assert "USER appuser" in content or re.search(
        r"USER\s+\d+", content
    ), "No non-root USER directive found"


def test_user_created():
    content = DOCKERFILE.read_text()
    assert "groupadd" in content or "addgroup" in content, "No user group created"
    assert "useradd" in content or "adduser" in content, "No user created"


# ── HEALTHCHECK ──

def test_healthcheck_present():
    content = DOCKERFILE.read_text()
    assert "HEALTHCHECK" in content, "HEALTHCHECK instruction missing"


def test_healthcheck_has_retries():
    content = DOCKERFILE.read_text()
    # --retries= may be anywhere in the HEALTHCHECK line, not immediately after HEALTHCHECK
    match = re.search(r"--retries=(\d+)", content)
    assert match and int(match.group(1)) > 0, "HEALTHCHECK missing --retries flag"


# ── Signal handling ──

def test_exec_form_cmd():
    content = DOCKERFILE.read_text()
    lines = content.strip().splitlines()
    # Find last CMD instruction and verify exec (json array) form
    last_cmd = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("CMD"):
            last_cmd = stripped
    assert last_cmd is not None, "No CMD instruction found"
    assert last_cmd.startswith("CMD ["), "CMD must use exec form (JSON array) for signal handling"


def test_graceful_shutdown():
    content = DOCKERFILE.read_text()
    assert "timeout-graceful-shutdown" in content or "graceful" in content.lower(), \
        "No graceful shutdown configuration found"


# ── Port & networking ──

def test_expose_port():
    content = DOCKERFILE.read_text()
    assert "EXPOSE 8000" in content or "EXPOSE 80" in content, \
        "EXPOSE instruction missing for application port"


def test_curl_healthcheck():
    content = DOCKERFILE.read_text()
    assert "curl" in content, \
        "HEALTHCHECK uses curl (expected for lightweight liveness)"


# ── Layer caching ──

def test_copy_requirements_before_code():
    """Verify requirements files are copied before app code (layer caching)."""
    content = DOCKERFILE.read_text()
    builder_section = content.split("AS builder")[1].split("AS")[0]
    # Find lines with COPY ...requirements
    req_lines = [i for i, line in enumerate(builder_section.splitlines())
                 if re.search(r"COPY.*requirements", line)]
    # Find lines with COPY  .  or COPY . .
    code_lines = [i for i, line in enumerate(builder_section.splitlines())
                  if re.search(r"COPY\s+\.\s", line)]
    # In the builder, we only COPY requirements, not the full app
    # The app code is copied in the runtime stage
    assert len(req_lines) >= 1, \
        "Builder stage must COPY requirements files first"
    # In the builder stage, COPY . should not appear before requirements
    if code_lines and req_lines:
        assert code_lines[0] > req_lines[-1], \
            "COPY . must not appear before COPY requirements in builder stage"
    # Verify runtime stage also puts COPY . after all other COPY instructions
    runtime_section = content.split("AS runtime")[1]
    # Find the line index of COPY . . in the runtime section
    runtime_req_lines = [i for i, line in enumerate(runtime_section.splitlines())
                         if re.search(r"COPY.*requirements", line)]
    runtime_code_lines = [i for i, line in enumerate(runtime_section.splitlines())
                          if re.search(r"COPY\s.*\.\s", line)]
    if runtime_code_lines:
        assert len(runtime_code_lines) == 1, \
            "There should be exactly one COPY . . in the runtime stage"
        if runtime_req_lines:
            assert runtime_code_lines[0] > runtime_req_lines[-1], \
                "COPY . must be after COPY requirements in runtime stage"


# ── Security ──

def test_no_root_user():
    content = DOCKERFILE.read_text()
    # Find USER directives after the builder stage
    runtime_section = content.split("AS runtime")[1] if "AS runtime" in content else content
    root_after = re.search(r"USER\s+root", runtime_section)
    assert root_after is None, "Runtime stage must not switch back to root user"


def test_slim_base_image():
    content = DOCKERFILE.read_text()
    assert "slim" in content, "Consider using -slim base image for smaller footprint"


# ── .dockerignore validation ──

def test_dockerignore_blocks_secrets():
    content = DOCKERIGNORE.read_text()
    assert ".env" in content, ".dockerignore should exclude .env files"
    assert "*.pem" in content or "*.key" in content, \
        ".dockerignore should exclude private keys"


def test_dockerignore_blocks_vcs():
    content = DOCKERIGNORE.read_text()
    assert ".git/" in content, ".dockerignore should exclude .git directory"


def test_dockerignore_blocks_cache():
    content = DOCKERIGNORE.read_text()
    assert "__pycache__" in content, ".dockerignore should exclude Python cache"
