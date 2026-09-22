# LAB 8 — the production image for the hardened server.
#
# Four hardening decisions live in this file, and each one is checked by
# M10_security/code/lab_10_container_smoke.py:
#
#   1. multi-stage build: the compiler, the build cache and the dev dependencies never ship
#   2. a dedicated NON-ROOT user owns the process (uid 10001) — a container escape starts
#      from `nobody`, not from `root`
#   3. the log directory is the ONLY writable path, mounted as a volume so it survives a restart
#   4. no secrets in the image and no network egress needed to start
#
# The base image tags are pinned. Re-pin them the day you build, and record it — a floating
# `:latest` in a security lesson is a contradiction.

# --- stage 1: resolve and install dependencies with uv -------------------------------
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy ONLY the lockfile inputs first: this layer is cached until a dependency changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Then the source. --frozen means the lockfile is truth; it never re-resolves inside the build.
COPY M10_security/ ./M10_security/
RUN uv sync --frozen --no-dev

# --- stage 2: the runtime image, with no build tools ----------------------------------
FROM python:3.11-slim AS runtime

# Unbuffered output so tool calls appear in `docker logs` as they happen, not at exit.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    LOG_ROOT=/var/log/mcp

# A fixed, high uid that will not collide with a host user. No shell login, no home directory
# writable by anyone else.
RUN groupadd --gid 10001 mcp \
 && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin mcp \
 && mkdir -p /var/log/mcp \
 && chown -R 10001:10001 /var/log/mcp

WORKDIR /app

# Copy the finished virtualenv and the source from the builder, owned by root and readable
# by the runtime user — the process can read code but cannot rewrite it.
COPY --from=builder --chown=0:0 /app/.venv /app/.venv
COPY --from=builder --chown=0:0 /app/M10_security /app/M10_security

# Drop privileges. Everything after this line runs as uid 10001.
USER 10001:10001

# The log directory is the only thing the tools may write, and it is the only volume.
VOLUME ["/var/log/mcp"]

# stdio is the default transport; an HTTP deployment would EXPOSE 8000 instead and put a
# reverse proxy in front. Never expose FastMCP directly to a network without that proxy.
ENTRYPOINT ["python", "-m", "M10_security.code.path_validation"]

# Labels make the artifact auditable after the fact: which commit, which lockfile, which build.
LABEL org.opencontainers.image.title="hardened-mcp-logs" \
      org.opencontainers.image.description="M10 hardened log reader — non-root, read-only rootfs" \
      org.opencontainers.image.source="https://example.invalid/fastmcp-course"
