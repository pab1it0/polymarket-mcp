#!/usr/bin/env python

import os
import json
import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import httpx

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Polymarket MCP")

@dataclass
class PolymarketConfig:
    api_url: str = "https://clob.polymarket.com"
    chain_id: int = 137  # Default to Polygon mainnet

# Load configuration from environment variables with defaults
config = PolymarketConfig(
    api_url=os.environ.get("POLYMARKET_API_URL", "https://clob.polymarket.com"),
    chain_id=int(os.environ.get("POLYMARKET_CHAIN_ID", "137")),
)

async def make_api_request(endpoint: str, params: Dict[str, Any] = None, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the Polymarket API."""
    url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params or {})
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data, params=params or {})
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()

@mcp.tool(description="Get a list of all available markets on Polymarket.")
async def get_markets(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get a list of all available markets.
    
    Parameters:
    - status: Filter markets by status (OPEN, RESOLVED, etc.)
    """
    params = {}
    if status:
        params["status"] = status
    
    response = await make_api_request("markets", params=params)
    return response.get("markets", [])

@mcp.tool(description="Get detailed information about a specific market by its ID.")
async def get_market_by_id(market_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific market.
    
    Parameters:
    - market_id: The unique identifier of the market
    """
    return await make_api_request(f"markets/{market_id}")

@mcp.tool(description="Get the current order book for a specific market.")
async def get_order_book(market_id: str, outcome_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current order book for a market.
    
    Parameters:
    - market_id: The unique identifier of the market
    - outcome_id: Optional outcome ID to filter by
    """
    params = {"marketId": market_id}
    if outcome_id:
        params["outcomeId"] = outcome_id
    
    return await make_api_request("orderbook", params=params)

@mcp.tool(description="Get the latest trades for a specific market.")
async def get_recent_trades(market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent trades for a market.
    
    Parameters:
    - market_id: The unique identifier of the market
    - limit: Maximum number of trades to return
    """
    params = {"marketId": market_id, "limit": limit}
    response = await make_api_request("trades", params=params)
    return response.get("trades", [])

@mcp.tool(description="Get historical market data (prices and volumes) for a specific market.")
async def get_market_history(market_id: str, resolution: str = "hour") -> List[Dict[str, Any]]:
    """
    Get historical market data.
    
    Parameters:
    - market_id: The unique identifier of the market
    - resolution: Time resolution (hour, day, week)
    """
    params = {"marketId": market_id, "resolution": resolution}
    response = await make_api_request("markets/history", params=params)
    return response.get("history", [])

@mcp.tool(description="Search for markets by keyword or phrase.")
async def search_markets(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for markets by keyword.
    
    Parameters:
    - query: Search term
    - limit: Maximum number of results to return
    """
    params = {"q": query, "limit": limit}
    response = await make_api_request("markets/search", params=params)
    return response.get("markets", [])

@mcp.resource("polymarket://markets")
async def markets_resource() -> str:
    """Resource that returns all available markets."""
    try:
        markets = await get_markets()
        return json.dumps(markets, indent=2)
    except Exception as e:
        return f"Error retrieving markets: {str(e)}"

@mcp.resource("polymarket://markets/{market_id}")
async def market_details_resource(market_id: str) -> str:
    """
    Resource that returns details for a specific market.
    
    Parameters:
    - market_id: The unique identifier of the market
    """
    try:
        market = await get_market_by_id(market_id=market_id)
        return json.dumps(market, indent=2)
    except Exception as e:
        return f"Error retrieving market details: {str(e)}"

@mcp.resource("polymarket://search/{query}")
async def search_markets_resource(query: str) -> str:
    """
    Resource that returns markets matching a search query.
    
    Parameters:
    - query: Search term
    """
    try:
        markets = await search_markets(query=query)
        return json.dumps(markets, indent=2)
    except Exception as e:
        return f"Error searching markets: {str(e)}"

if __name__ == "__main__":
    sys.stderr.write(f"Starting Polymarket MCP Server...\n")
    mcp.run()
