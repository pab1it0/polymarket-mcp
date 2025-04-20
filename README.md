# Polymarket MCP Server

A [Model Context Protocol][mcp] (MCP) server for Polymarket's Gamma Markets API.

This provides access to Polymarket's prediction markets and market data through standardized MCP interfaces, allowing AI assistants to query market data and analyze prediction markets.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Market and Event data access
  - [x] List all available markets and events with extensive filtering options
  - [x] Get detailed market and event information
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

#### Building and Running with Docker

To build and run the Docker image locally:

```bash
# Build the Docker image
docker build -t polymarket-mcp-server .

# Run the container
docker run -it --rm \
  -e GAMMA_API_URL=https://gamma-api.polymarket.com \
  -e GAMMA_REQUIRES_AUTH=false \
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
        "-e", "GAMMA_API_URL",
        "-e", "GAMMA_REQUIRES_AUTH",
        "polymarket-mcp-server"
      ],
      "env": {
        "GAMMA_API_URL": "https://gamma-api.polymarket.com",
        "GAMMA_REQUIRES_AUTH": "false"
      }
    }
  }
}
```

### Running with uv (Alternative Method)

If you prefer not to use Docker, you can use `uv` to run the server directly.

1. Create and configure a `.env` file in the project root directory:

```bash
# Copy the template
cp .env.template .env

# Edit the file to add your configuration
nano .env
```

Example `.env` content:

```env
# Polymarket Gamma API Configuration
GAMMA_API_URL=https://gamma-api.polymarket.com
GAMMA_REQUIRES_AUTH=false
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
        "GAMMA_API_URL": "https://gamma-api.polymarket.com",
        "GAMMA_REQUIRES_AUTH": "false"
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

### Environment Variables Support

The server loads environment variables from a `.env` file in the project root directory if present. Copy `.env.template` to `.env` and adjust the values as needed.

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
├── .env.template            # Template for environment variables
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
| `get_markets` | Market Data | Get a list of all available markets with comprehensive filtering options |
| `get_market_by_id` | Market Data | Get detailed information about a specific market |
| `get_order_book` | Market Data | [EXPERIMENTAL] Get the current order book for a market |
| `get_recent_trades` | Market Data | [EXPERIMENTAL] Get latest trades for a market |
| `get_market_history` | Market Data | [EXPERIMENTAL] Get historical market data |
| `search_markets` | Market Data | Search for markets by keyword using slug filtering |
| `get_events` | Event Data | Get a list of all available events with comprehensive filtering options |
| `get_event_by_id` | Event Data | Get detailed information about a specific event |

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
