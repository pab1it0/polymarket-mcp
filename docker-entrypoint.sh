#!/bin/sh
set -e

# Run the Polymarket MCP server
exec polymarket-mcp-server "$@"
