# syntax=docker.io/docker/dockerfile:1.7-labs

FROM ghcr.io/astral-sh/uv:0.11.32 AS uv

FROM python:3.14-slim AS base

# ENVs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /srv/app

##################################################

FROM base AS builder

# Install dependencies first (without installing the project itself).
RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --frozen --no-install-project --no-group dev

# Copy the project into the image — no src/, files are at root.
COPY ./ ./

# Sync the project now that sources exist.
RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-group dev

##################################################

FROM base AS runtime

# Run as a non-root user.
RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

# Copy venv and app files from builder stage.
COPY --from=builder /srv/app/.venv/ /srv/app/.venv/
COPY --from=builder /srv/app/telegram_file_sender/ ./telegram_file_sender/

ENV PATH="/srv/app/.venv/bin:$PATH"

ENTRYPOINT [ "python3", "-m", "telegram_file_sender" ]
