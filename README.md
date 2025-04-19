# Polymarket MCP Server

A [Model Context Protocol][mcp] (MCP) server for Polymarket prediction markets platform.

This provides access to Polymarket's prediction markets and market data through standardized MCP interfaces, allowing AI assistants to query market data and analyze prediction markets.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Market data access
  - [x] List all available markets
  - [x] Get detailed market information
  - [x] Search markets by keyword
  - [x] Get order book data
  - [x] View recent trades
  - [x] Get historical market data

- [x] Docker containerization support

- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.
This is useful if you don't use certain functionality or if you don't want to take up too much of the context window.

## Usage

### Docker Usage (Recommended)

Docker provides the most reliable and consistent way to run the Polymarket MCP server across different environments.

#### Using Pre-built Docker Image

The easiest way to run the Polymarket MCP server is to use the pre-built Docker image from GitHub Container Registry:

```bash
docker run -it --rm \
  -e POLYMARKET_API_URL=https://clob.polymarket.com \
  -e POLYMARKET_CHAIN_ID=137 \
  ghcr.io/pab1it0/polymarket-mcp:latest
```

#### Building the Docker Image Locally

Alternatively, you can build the Docker image locally:

```bash
docker build -t polymarket-mcp-server .
```

And then run it:

```bash
docker run -it --rm \
  -e POLYMARKET_API_URL=https://clob.polymarket.com \
  -e POLYMARKET_CHAIN_ID=137 \
  polymarket-mcp-server
```

#### Running with Docker in Claude Desktop

To use the containerized server with Claude Desktop, add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "POLYMARKET_API_URL",
        "-e", "POLYMARKET_CHAIN_ID",
        "ghcr.io/pab1it0/polymarket-mcp:latest"
      ],
      "env": {
        "POLYMARKET_API_URL": "https://clob.polymarket.com",
        "POLYMARKET_CHAIN_ID": "137"
      }
    }
  }
}
```

This configuration passes the environment variables from Claude Desktop to the Docker container by using the `-e` flag with just the variable name, and providing the actual values in the `env` object.

### Running with uv (Alternative Method)

If you prefer not to use Docker, you can use `uv` to run the server directly.

1. Configure the environment variables:

```env
# Polymarket API configuration
POLYMARKET_API_URL=https://clob.polymarket.com
POLYMARKET_CHAIN_ID=137  # Polygon mainnet
```

2. Add the server configuration to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "/usr/local/bin/uv",  // Use the full path to your uv installation
      "args": [
        "run",
        "-m", "polymarket_mcp_server.main"
      ],
      "cwd": "<full path to polymarket-mcp directory>",
      "env": {
        "POLYMARKET_API_URL": "https://clob.polymarket.com",
        "POLYMARKET_CHAIN_ID": "137"
      }
    }
  }
}
```

> Note: If you see `Error: spawn uv ENOENT` in Claude Desktop, you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

## Project Structure

The project has been organized with a `src` directory structure:

```
polymarket-mcp/
├── src/
│   └── polymarket_mcp_server/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation
│       └── main.py          # Main application logic
├── Dockerfile               # Docker configuration
├── .dockerignore            # Docker ignore file
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Testing

The project includes a comprehensive test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

Tests are organized into:
- Server functionality tests
- Main application tests
- Error handling tests

When adding new features, please also add corresponding tests.

### Available Tools

| Tool | Category | Description |
| --- | --- | --- |
| `get_markets` | Market Data | Get a list of all available markets |
| `get_market_by_id` | Market Data | Get detailed information about a specific market |
| `get_order_book` | Market Data | Get the current order book for a market |
| `get_recent_trades` | Market Data | Get latest trades for a market |
| `get_market_history` | Market Data | Get historical market data |
| `search_markets` | Market Data | Search for markets by keyword |

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
