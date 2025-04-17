#!/usr/bin/env python
import sys
import dotenv
import os
from polymarket_mcp_server.server import mcp, config

# Redirect stdout to a file to ensure only mcp.run uses it
# This is a crucial step to ensure the MCP communication is clean
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "polymarket_mcp.log")
sys.stderr = open(log_file, "a")

def setup_environment():
    if dotenv.load_dotenv():
        print("Loaded environment variables from .env file", file=sys.stderr)
    else:
        print("No .env file found or could not load it - using environment variables", file=sys.stderr)

    if not config.api_url:
        print("WARNING: POLYMARKET_API_URL environment variable is not set", file=sys.stderr)
        print("Using default API URL: https://clob.polymarket.com", file=sys.stderr)
    
    # Output configuration
    print(f"Polymarket API configuration:", file=sys.stderr)
    print(f"  API URL: {config.api_url}", file=sys.stderr)
    print(f"  Chain ID: {config.chain_id}", file=sys.stderr)
    
    return True

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Polymarket MCP Server...", file=sys.stderr)
    print("Running server in standard mode...", file=sys.stderr)
    
    # Run the server with the stdio transport
    # This will take over stdout for JSON communication
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
