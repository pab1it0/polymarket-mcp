#!/usr/bin/env python

import os
import json
import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file (silently continues if no file found)
try:
    load_dotenv()
except Exception:
    pass

mcp = FastMCP("Polymarket MCP")

@dataclass
class GammaConfig:
    api_url: str = "https://gamma-api.polymarket.com"
    requires_auth: bool = False

# Load configuration from environment variables with defaults
config = GammaConfig(
    api_url=os.environ.get("GAMMA_API_URL", "https://gamma-api.polymarket.com"),
    requires_auth=os.environ.get("GAMMA_REQUIRES_AUTH", "false").lower() == "true"
)

async def make_api_request(endpoint: str, params: Dict[str, Any] = None, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the Polymarket Gamma API."""
    url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    
    # Add authentication if needed in the future
    if config.requires_auth:
        # Implementation would depend on Gamma API auth requirements
        pass
    
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
async def get_markets(status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a list of all available markets.
    
    Parameters:
    - status: Filter markets by status (active, closed, archived)
    """
    try:
        params = {}
        if status:
            if status.lower() == "open":
                params["active"] = True
            elif status.lower() == "closed":
                params["closed"] = True
            elif status.lower() == "archived":
                params["archived"] = True
        
        response = await make_api_request("markets", params=params)
        return response
    except Exception as e:
        sys.stderr.write(f"Error getting markets: {str(e)}\n")
        return {"markets": []}

@mcp.tool(description="Get detailed information about a specific market by its ID.")
async def get_market_by_id(market_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific market.
    
    Parameters:
    - market_id: The unique identifier of the market
    """
    try:
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
        # Note: This endpoint was not explicitly mentioned in the Gamma API docs
        # We're making an assumption about its availability and format
        # May need to be updated based on actual Gamma API implementation
        params = {}
        if outcome_id:
            params["outcome_id"] = outcome_id
            
        return await make_api_request(f"markets/{market_id}/orderbook", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting order book: {str(e)}\n")
        return {"error": str(e)}

@mcp.tool(description="Get the latest trades for a specific market.")
async def get_recent_trades(market_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get recent trades for a market.
    
    Parameters:
    - market_id: The unique identifier of the market
    - limit: Maximum number of trades to return
    """
    try:
        # Note: This endpoint was not explicitly mentioned in the Gamma API docs
        # We're making an assumption about its availability and format
        params = {"limit": limit}
        return await make_api_request(f"markets/{market_id}/trades", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting recent trades: {str(e)}\n")
        return {"trades": []}

@mcp.tool(description="Get historical market data (prices and volumes) for a specific market.")
async def get_market_history(market_id: str, resolution: str = "hour") -> Dict[str, Any]:
    """
    Get historical market data.
    
    Parameters:
    - market_id: The unique identifier of the market
    - resolution: Time resolution (hour, day, week)
    """
    try:
        # Note: This endpoint was not explicitly mentioned in the Gamma API docs
        # We're making an assumption about its availability and format
        params = {"resolution": resolution}
        return await make_api_request(f"markets/{market_id}/history", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting market history: {str(e)}\n")
        return {"history": []}

@mcp.tool(description="Search for markets by keyword or phrase.")
async def search_markets(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for markets by keyword.
    
    Parameters:
    - query: Search term
    - limit: Maximum number of results to return
    """
    try:
        # Using the slug parameter for search, as the documentation doesn't 
        # explicitly mention a search endpoint
        params = {"slug": query, "limit": limit}
        return await make_api_request("markets", params=params)
    except Exception as e:
        sys.stderr.write(f"Error searching markets: {str(e)}\n")
        return {"markets": []}

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

# New resources for events based on Gamma API
@mcp.tool(description="Get a list of all available events on Polymarket.")
async def get_events(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    active: Optional[bool] = None,
    closed: Optional[bool] = None,
    archived: Optional[bool] = None,
    tag: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a list of all available events.
    
    Parameters:
    - limit: Maximum number of events to return
    - offset: Number of events to skip (for pagination)
    - active: Filter by active status
    - closed: Filter by closed status
    - archived: Filter by archived status
    - tag: Filter by tag label
    """
    try:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if active is not None:
            params["active"] = active
        if closed is not None:
            params["closed"] = closed
        if archived is not None:
            params["archived"] = archived
        if tag:
            params["tag"] = tag
            
        return await make_api_request("events", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting events: {str(e)}\n")
        return {"events": []}

@mcp.tool(description="Get detailed information about a specific event by its ID.")
async def get_event_by_id(event_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific event.
    
    Parameters:
    - event_id: The unique identifier of the event
    """
    try:
        return await make_api_request(f"events/{event_id}")
    except Exception as e:
        sys.stderr.write(f"Error getting event details: {str(e)}\n")
        return {"error": str(e)}

@mcp.resource("polymarket://events")
async def events_resource() -> str:
    """Resource that returns all available events."""
    try:
        events = await get_events()
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error retrieving events: {str(e)}"

@mcp.resource("polymarket://events/{event_id}")
async def event_details_resource(event_id: str) -> str:
    """
    Resource that returns details for a specific event.
    
    Parameters:
    - event_id: The unique identifier of the event
    """
    try:
        event = await get_event_by_id(event_id=event_id)
        return json.dumps(event, indent=2)
    except Exception as e:
        return f"Error retrieving event details: {str(e)}"

if __name__ == "__main__":
    sys.stderr.write(f"Starting Polymarket MCP Server with Gamma API...\n")
    mcp.run()
