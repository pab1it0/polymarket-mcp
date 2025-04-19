#!/usr/bin/env python
import sys
from polymarket_mcp_server.server import mcp, config

def setup_environment():
    print("Using environment variables for configuration")

    print(f"Polymarket API configuration:")
    print(f"  API URL: {config.api_url}")
    print(f"  Chain ID: {config.chain_id}")
    
    return True

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Polymarket MCP Server...")
    print("Running server in standard mode...")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
