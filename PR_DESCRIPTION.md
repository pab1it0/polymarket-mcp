# Fix MCP JSON Communication Issues

## Problem

When running the Polymarket MCP server with Claude Desktop, the system was encountering JSON parsing errors:

```
Unexpected token 'N', "No .env fi"... is not valid JSON
Unexpected token 'P', "Polymarket"... is not valid JSON
Unexpected token 'A', "  API URL: h"... is not valid JSON
```

These errors occurred because standard output messages were interfering with the MCP protocol's JSON-RPC communication.

## Solution

This PR simplifies the server implementation to match the approach used in the working adx-mcp-server:

1. Removed complex logging configurations and stdout/stderr redirections
2. Reverted to simple print statements that the MCP library can handle internally
3. Simplified the Docker configuration

## Implementation Details

- Updated main.py to use direct print statements (matching adx-mcp-server)
- Modified server.py to remove custom logging configuration
- Simplified the Dockerfile by removing unnecessary log directory creation

## Testing

The changes have been tested with Claude Desktop, and the server now communicates properly without JSON parsing errors.

## References

The implementation is based on the working approach used in the adx-mcp-server repository, which successfully handles the MCP protocol communication.
