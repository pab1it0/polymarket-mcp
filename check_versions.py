#!/usr/bin/env python
import sys
import importlib

try:
    import mcp
    print(f"MCP version: {mcp.__version__}")
except (ImportError, AttributeError) as e:
    print(f"Could not get MCP version: {e}")

try:
    from mcp.server.fastmcp import FastMCP
    print(f"FastMCP class available")
except ImportError as e:
    print(f"Could not import FastMCP: {e}")

print(f"Python version: {sys.version}")
