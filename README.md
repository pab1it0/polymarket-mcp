# Polymarket MCP Server

A [Model Context Protocol][mcp] (MCP) server for Polymarket prediction markets platform.

This provides access to Polymarket's prediction markets, trading capabilities, and market data through standardized MCP interfaces, allowing AI assistants to query market data, place trades, and manage portfolios.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Market data access
  - [x] List all available markets
  - [x] Get detailed market information
  - [x] Search markets by keyword
  - [x] Get order book data
  - [x] View recent trades
  - [x] Get historical market data

- [x] Trading capabilities (with authentication)
  - [x] Create buy/sell orders
  - [x] Cancel orders
  - [x] View user orders
  - [x] Get portfolio positions

- [x] Authentication support
  - [x] Private key-based authentication
  - [x] API credentials generation

- [x] Docker containerization support

## Usage

1. Configure the environment variables for your Polymarket access, either through a `.env` file or system environment variables:

```env
# Required: Polymarket API configuration
POLYMARKET_API_URL=https://clob.polymarket.com
POLYMARKET_CHAIN_ID=137

# Optional: For authentication (required for trading)
POLYMARKET_PRIVATE_KEY=your_polygon_wallet_private_key
POLYMARKET_USE_AUTH=true
```

2. Add the server configuration to your client configuration file. For example, for Claude Desktop:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to polymarket-mcp directory>",
        "run",
        "src/polymarket_mcp_server/main.py"
      ],
      "env": {
        "POLYMARKET_API_URL": "https://clob.polymarket.com",
        "POLYMARKET_CHAIN_ID": "137",
        "POLYMARKET_PRIVATE_KEY": "your_polygon_wallet_private_key",
        "POLYMARKET_USE_AUTH": "true"
      }
    }
  }
}
```

> Note: If you see `Error: spawn uv ENOENT` in Claude Desktop, you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

## Docker Usage

This project includes Docker support for easy deployment and isolation.

### Building the Docker Image

Build the Docker image using:

```bash
docker build -t polymarket-mcp-server .
```

### Running with Docker

You can run the server using Docker in several ways:

#### Using docker run directly:

```bash
docker run -it --rm \
  -e POLYMARKET_API_URL=https://clob.polymarket.com \
  -e POLYMARKET_CHAIN_ID=137 \
  -e POLYMARKET_PRIVATE_KEY=your_polygon_wallet_private_key \
  polymarket-mcp-server
```

#### Using docker-compose:

Create a `.env` file with your Polymarket credentials and then run:

```bash
docker-compose up
```

### Running with Docker in Claude Desktop

To use the containerized server with Claude Desktop, update the configuration to use Docker with the environment variables:

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
        "-e", "POLYMARKET_PRIVATE_KEY",
        "-e", "POLYMARKET_USE_AUTH",
        "polymarket-mcp-server"
      ],
      "env": {
        "POLYMARKET_API_URL": "https://clob.polymarket.com",
        "POLYMARKET_CHAIN_ID": "137",
        "POLYMARKET_PRIVATE_KEY": "your_polygon_wallet_private_key",
        "POLYMARKET_USE_AUTH": "true"
      }
    }
  }
}
```

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
│       ├── main.py          # Main application logic
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore            # Docker ignore file
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Testing

The project includes a test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

## Available Tools

| Tool | Category | Description |
| --- | --- | --- |
| `get_markets` | Market Data | Get a list of all available markets |
| `get_market_by_id` | Market Data | Get detailed information about a specific market |
| `get_order_book` | Market Data | Get the current order book for a market |
| `get_recent_trades` | Market Data | Get latest trades for a market |
| `get_market_history` | Market Data | Get historical market data |
| `search_markets` | Market Data | Search for markets by keyword |
| `get_account_info` | Account | Get user account information (authenticated) |
| `get_user_orders` | Trading | Get a user's orders (authenticated) |
| `create_order` | Trading | Create a new buy/sell order (authenticated) |
| `cancel_order` | Trading | Cancel an existing order (authenticated) |
| `get_portfolio` | Portfolio | Get user portfolio positions (authenticated) |

## Security Considerations

- **Private Keys**: Your private key is used to generate API credentials. Keep it secure and never share it.
- **Environment Variables**: Use environment variables or `.env` files to configure sensitive information.
- **Permissions**: The MCP server only exposes the functionalities needed. Authentication is required for trading.

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
