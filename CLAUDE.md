# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server that wraps Polymarket's Gamma Markets API, exposing prediction market data as MCP tools and resources for AI assistants like Claude Desktop.

## Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/unit/test_server.py::test_function_name

# Run with coverage (default via pyproject.toml addopts)
pytest --cov=src --cov-report=term-missing

# Lint
flake8 src tests

# Run server directly
uv run -m polymarket_mcp_server.main

# Build Docker image
docker build -t polymarket-mcp-server .
```

## Architecture

- **`src/polymarket_mcp_server/server.py`** — Core file. Defines the `FastMCP` server instance (`mcp`), all MCP tools (`@mcp.tool`) and resources (`@mcp.resource`), the `GammaConfig` dataclass, and the `make_api_request` helper. All API calls go through `make_api_request` which uses `httpx.AsyncClient` against the Gamma API.
- **`src/polymarket_mcp_server/main.py`** — Entry point. Imports `mcp` and `config` from `server.py`, sets up environment via `dotenv`, and runs `mcp.run(transport="stdio")`.
- **Tools** are async functions decorated with `@mcp.tool` in `server.py`. They correspond to Gamma API endpoints (`/markets`, `/events`, etc.).
- **Resources** are `@mcp.resource` decorated functions that return JSON strings, wrapping the tool functions.

## Key Details

- Python >=3.10, uses `uv` for dependency management
- Config via environment variables: `GAMMA_API_URL` (default: `https://gamma-api.polymarket.com`), `GAMMA_REQUIRES_AUTH` (default: `false`)
- `.env` file support via `python-dotenv` (copy `.env.template` to `.env`)
- Server communicates over stdio transport (MCP protocol)
- Tests use `pytest-asyncio` and `pytest-mock`; test files are in `tests/` and `tests/unit/`
