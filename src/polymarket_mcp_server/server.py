#!/usr/bin/env python

import os
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import dotenv
import requests
import aiohttp
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
mcp = FastMCP("Polymarket MCP")

@dataclass
class PolymarketConfig:
    api_url: str
    chain_id: int

# Load configuration from environment variables with defaults
config = PolymarketConfig(
    api_url=os.environ.get("POLYMARKET_API_URL", "https://clob.polymarket.com"),
    chain_id=int(os.environ.get("POLYMARKET_CHAIN_ID", "137")),  # Default to Polygon mainnet
)

async def make_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a request to the Polymarket API."""
    url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    
    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Request failed with status {response.status}: {error_text}")
                    return await response.json()
            elif method == "POST":
                async with session.post(url, headers=headers, json=data, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Request failed with status {response.status}: {error_text}")
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {e}")
        raise ValueError(f"Failed to communicate with Polymarket API: {e}")

@mcp.tool(description="Get a list of all available markets on Polymarket.")
async def get_markets(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get a list of all available markets.
    
    Args:
        status: Filter markets by status (OPEN, RESOLVED, etc.)
    
    Returns:
        List of market information
    """
    params = {}
    if status:
        params["status"] = status
    
    response = await make_request("/markets", params=params)
    return response.get("markets", [])

@mcp.tool(description="Get detailed information about a specific market by its ID.")
async def get_market_by_id(market_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific market.
    
    Args:
        market_id: The unique identifier of the market
    
    Returns:
        Market details
    """
    response = await make_request(f"/markets/{market_id}")
    return response

@mcp.tool(description="Get the current order book for a specific market.")
async def get_order_book(market_id: str, outcome_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current order book for a market.
    
    Args:
        market_id: The unique identifier of the market
        outcome_id: Optional outcome ID to filter by
    
    Returns:
        Order book data
    """
    params = {"marketId": market_id}
    if outcome_id:
        params["outcomeId"] = outcome_id
    
    response = await make_request("/orderbook", params=params)
    return response

@mcp.tool(description="Get the latest trades for a specific market.")
async def get_recent_trades(market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent trades for a market.
    
    Args:
        market_id: The unique identifier of the market
        limit: Maximum number of trades to return
    
    Returns:
        List of recent trades
    """
    params = {"marketId": market_id, "limit": limit}
    response = await make_request("/trades", params=params)
    return response.get("trades", [])

@mcp.tool(description="Get historical market data (prices and volumes) for a specific market.")
async def get_market_history(market_id: str, resolution: str = "hour") -> List[Dict[str, Any]]:
    """
    Get historical market data.
    
    Args:
        market_id: The unique identifier of the market
        resolution: Time resolution (hour, day, week)
    
    Returns:
        Historical market data
    """
    params = {"marketId": market_id, "resolution": resolution}
    response = await make_request("/markets/history", params=params)
    return response.get("history", [])

@mcp.tool(description="Search for markets by keyword or phrase.")
async def search_markets(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for markets by keyword.
    
    Args:
        query: Search term
        limit: Maximum number of results to return
    
    Returns:
        List of matching markets
    """
    params = {"q": query, "limit": limit}
    response = await make_request("/markets/search", params=params)
    return response.get("markets", [])

if __name__ == "__main__":
    print(f"Starting Polymarket MCP Server...")
    mcp.run()
