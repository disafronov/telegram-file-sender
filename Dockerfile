# syntax=docker.io/docker/dockerfile:1.7-labs

FROM python:3.13.2-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /srv/app

##################################################

FROM base AS builder

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
  python3 -m venv /opt/venv && \
  pip3 install --ignore-installed --no-cache-dir --disable-pip-version-check --upgrade pip setuptools wheel && \
  pip3 install --ignore-installed --no-cache-dir -r requirements.txt

##################################################

FROM base AS runtime

COPY --from=builder /opt/venv/ /opt/venv/

COPY --exclude=requirements.txt ./ ./

ENTRYPOINT [ "python3", "-m", "telegram_file_sender" ]
