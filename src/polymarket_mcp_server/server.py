#!/usr/bin/env python

import os
import json
import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Load environment variables from .env file (silently continues if no file found)
try:
    load_dotenv()
except Exception:
    pass

mcp = FastMCP("Polymarket MCP")

@dataclass
class PolymarketConfig:
    api_url: str = "https://clob.polymarket.com"
    chain_id: int = 137  # Default to Polygon mainnet
    key: Optional[str] = None
    funder: Optional[str] = None
    requires_auth: bool = True

# Load configuration from environment variables with defaults
config = PolymarketConfig(
    api_url=os.environ.get("POLYMARKET_API_URL", "https://clob.polymarket.com"),
    chain_id=int(os.environ.get("POLYMARKET_CHAIN_ID", "137")),
    key=os.environ.get("KEY"),
    funder=os.environ.get("FUNDER"),
    requires_auth=os.environ.get("POLYMARKET_REQUIRES_AUTH", "true").lower() == "true"
)

# Initialize the CLOB client
def get_clob_client() -> Optional[ClobClient]:
    """Get an initialized CLOB client if authentication is available."""
    try:
        if config.key and config.funder:
            client = ClobClient(
                config.api_url,
                key=config.key,
                chain_id=POLYGON,
                funder=config.funder,
                signature_type=1,
            )
            client.set_api_creds(client.create_or_derive_api_creds())
            return client
        else:
            # Return a client without authentication for read-only operations
            client = ClobClient(config.api_url, chain_id=POLYGON)
            return client
    except Exception as e:
        sys.stderr.write(f"Error initializing CLOB client: {str(e)}\n")
        return None

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
    try:
        client = get_clob_client()
        if client:
            markets_data = client.get_markets()
            
            # Filter by status if specified
            if status and isinstance(markets_data, list):
                markets_data = [
                    market for market in markets_data 
                    if isinstance(market, dict) and market.get('status', '').lower() == status.lower()
                ]
            
            return markets_data
        else:
            # Fallback to httpx request if client initialization failed
            params = {}
            if status:
                params["status"] = status
            
            response = await make_api_request("markets", params=params)
            return response.get("markets", [])
    except Exception as e:
        sys.stderr.write(f"Error getting markets: {str(e)}\n")
        return []

@mcp.tool(description="Get detailed information about a specific market by its ID.")
async def get_market_by_id(market_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific market.
    
    Parameters:
    - market_id: The unique identifier of the market
    """
    try:
        client = get_clob_client()
        if client:
            return client.get_market(market_id)
        else:
            # Fallback to httpx request if client initialization failed
            return await make_api_request(f"markets/{market_id}")
    except Exception as e:
        sys.stderr.write(f"Error getting market details: {str(e)}\n")
        return {"error": str(e)}

@mcp.tool(description="Get the current order book for a specific market.")
async def get_order_book(market_id: str, outcome_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current order book for a market.
    
    Parameters:
    - market_id: The unique identifier of the market
    - outcome_id: Optional outcome ID to filter by
    """
    try:
        client = get_clob_client()
        if client:
            params = {"marketId": market_id}
            if outcome_id:
                params["outcomeId"] = outcome_id
            return client.get_orderbook(market_id, outcome_id)
        else:
            # Fallback to httpx request if client initialization failed
            params = {"marketId": market_id}
            if outcome_id:
                params["outcomeId"] = outcome_id
            
            return await make_api_request("orderbook", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting order book: {str(e)}\n")
        return {"error": str(e)}

@mcp.tool(description="Get the latest trades for a specific market.")
async def get_recent_trades(market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent trades for a market.
    
    Parameters:
    - market_id: The unique identifier of the market
    - limit: Maximum number of trades to return
    """
    try:
        client = get_clob_client()
        if client:
            trades = client.get_trades(market_id, limit=limit)
            return trades.get("trades", []) if isinstance(trades, dict) else trades
        else:
            # Fallback to httpx request if client initialization failed
            params = {"marketId": market_id, "limit": limit}
            response = await make_api_request("trades", params=params)
            return response.get("trades", [])
    except Exception as e:
        sys.stderr.write(f"Error getting recent trades: {str(e)}\n")
        return []

@mcp.tool(description="Get historical market data (prices and volumes) for a specific market.")
async def get_market_history(market_id: str, resolution: str = "hour") -> List[Dict[str, Any]]:
    """
    Get historical market data.
    
    Parameters:
    - market_id: The unique identifier of the market
    - resolution: Time resolution (hour, day, week)
    """
    try:
        client = get_clob_client()
        if client:
            history = client.get_market_history(market_id, resolution=resolution)
            return history.get("history", []) if isinstance(history, dict) else history
        else:
            # Fallback to httpx request if client initialization failed
            params = {"marketId": market_id, "resolution": resolution}
            response = await make_api_request("markets/history", params=params)
            return response.get("history", [])
    except Exception as e:
        sys.stderr.write(f"Error getting market history: {str(e)}\n")
        return []

@mcp.tool(description="Search for markets by keyword or phrase.")
async def search_markets(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for markets by keyword.
    
    Parameters:
    - query: Search term
    - limit: Maximum number of results to return
    """
    try:
        client = get_clob_client()
        if client:
            # Use the appropriate search method from py_clob_client
            # Note: This is a placeholder, adjust based on actual API
            markets = client.search_markets(query, limit=limit)
            return markets.get("markets", []) if isinstance(markets, dict) else markets
        else:
            # Fallback to httpx request if client initialization failed
            params = {"q": query, "limit": limit}
            response = await make_api_request("markets/search", params=params)
            return response.get("markets", [])
    except Exception as e:
        sys.stderr.write(f"Error searching markets: {str(e)}\n")
        return []

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
