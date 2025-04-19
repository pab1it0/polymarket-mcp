FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml ./
COPY uv.lock ./
COPY src ./src/

RUN uv venv && \
    uv pip install -e .

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml /app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PYTHONFAULTHANDLER=1

USER app

CMD ["/app/.venv/bin/polymarket-mcp-server"]

# GitHub Container Registry Metadata
LABEL org.opencontainers.image.title="Polymarket MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Polymarket integration" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Pavel Shklovsky" \
      org.opencontainers.image.source="https://github.com/pab1it0/polymarket-mcp" \
      org.opencontainers.image.url="https://github.com/pab1it0/polymarket-mcp" \
      org.opencontainers.image.licenses="MIT"
