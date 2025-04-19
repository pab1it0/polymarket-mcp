#!/usr/bin/env python
import sys
import os
from dotenv import load_dotenv
from polymarket_mcp_server.server import mcp, config

def setup_environment():
    # Load environment variables from .env file
    try:
        load_dotenv()
        sys.stderr.write("Loaded environment variables from .env file\n")
    except Exception as e:
        sys.stderr.write(f"Note: .env file not loaded, using default environment variables: {str(e)}\n")
    
    sys.stderr.write("Using environment variables for configuration\n")
    sys.stderr.write(f"Polymarket Gamma API configuration:\n")
    sys.stderr.write(f"  API URL: {config.api_url}\n")
    
    # Check if authentication is required and available (for future use)
    if config.requires_auth:
        sys.stderr.write("\nWarning: Authentication required but not implemented for Gamma API.\n")
        sys.stderr.write("Some API functions that require authentication may not work.\n")
    
    return True

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    sys.stderr.write("\nStarting Polymarket MCP Server with Gamma API...\n")
    sys.stderr.write("Running server in standard mode...\n")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
