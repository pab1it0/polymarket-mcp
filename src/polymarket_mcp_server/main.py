#!/usr/bin/env python
import sys
import os
import dotenv
from polymarket_mcp_server.server import mcp, config

# Custom implementation to suppress prints once MCP starts
class NullWriter:
    def write(self, text):
        pass
    def flush(self):
        pass

def setup_environment():
    if dotenv.load_dotenv():
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found or could not load it - using environment variables")

    if not config.api_url:
        print("WARNING: POLYMARKET_API_URL environment variable is not set")
        print("Using default API URL: https://clob.polymarket.com")
    
    # Output configuration
    print(f"Polymarket API configuration:")
    print(f"  API URL: {config.api_url}")
    print(f"  Chain ID: {config.chain_id}")
    
    return True

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Polymarket MCP Server...")
    print("Running server in standard mode...")
    
    # Disable further print output to avoid interfering with MCP
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    # Redirect stdout and stderr to null for print statements
    # but let MCP handle its own stdio communication
    sys.stdout = NullWriter()
    sys.stderr = NullWriter()
    
    # Run the server with the stdio transport
    try:
        mcp.run(transport="stdio")
    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

if __name__ == "__main__":
    run_server()
