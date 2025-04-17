#!/usr/bin/env python
import sys
import dotenv
from polymarket_mcp_server.server import mcp, config

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
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
