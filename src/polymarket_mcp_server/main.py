#!/usr/bin/env python
import sys
from polymarket_mcp_server.server import mcp, config

def setup_environment():
    sys.stderr.write("Using environment variables for configuration\n")
    sys.stderr.write(f"Polymarket API configuration:\n")
    sys.stderr.write(f"  API URL: {config.api_url}\n")
    sys.stderr.write(f"  Chain ID: {config.chain_id}\n")
    
    return True

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    sys.stderr.write("\nStarting Polymarket MCP Server...\n")
    sys.stderr.write("Running server in standard mode...\n")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
