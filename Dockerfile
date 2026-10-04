# Stage 1: Build & Dependency Resolution using Astral's uv
FROM python:3.12-slim-bookworm AS builder

# Install uv from official binary image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml README.md uv.lock* ./

# Install project dependencies
RUN uv pip install --system --no-cache -e .

# Copy application source code
COPY apps/ ./apps/
COPY core/ ./core/
COPY db/ ./db/
COPY memory/ ./memory/
COPY agents/ ./agents/
COPY workflows/ ./workflows/
COPY tools/ ./tools/
COPY evaluation/ ./evaluation/
COPY sandbox/ ./sandbox/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Stage 2: Runtime Image
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install runtime utilities for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create unprivileged application user
RUN groupadd -g 1001 morrow && \
    useradd -u 1001 -g morrow -s /bin/bash -m morrow

# Copy installed python site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=morrow:morrow /app /app

USER morrow

EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
