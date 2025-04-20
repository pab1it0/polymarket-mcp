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

@mcp.tool(description="Get a list of all available markets on Polymarket with comprehensive filtering options.")
async def get_markets(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order: Optional[str] = None,
    ascending: Optional[bool] = None,
    id: Optional[Union[int, List[int]]] = None,
    slug: Optional[Union[str, List[str]]] = None,
    archived: Optional[bool] = None,
    active: Optional[bool] = None,
    closed: Optional[bool] = None,
    clob_token_ids: Optional[Union[str, List[str]]] = None,
    condition_ids: Optional[Union[str, List[str]]] = None,
    liquidity_num_min: Optional[float] = None,
    liquidity_num_max: Optional[float] = None,
    volume_num_min: Optional[float] = None,
    volume_num_max: Optional[float] = None,
    start_date_min: Optional[str] = None,
    start_date_max: Optional[str] = None,
    end_date_min: Optional[str] = None,
    end_date_max: Optional[str] = None,
    tag_id: Optional[int] = None,
    related_tags: Optional[bool] = None,
    status: Optional[str] = None  # Keep for backward compatibility
) -> Dict[str, Any]:
    """
    Get a list of all available markets with extensive filtering options.
    
    Parameters:
    - limit: Maximum number of markets to return
    - offset: Number of markets to skip (for pagination)
    - order: Field to sort by
    - ascending: Sort direction (true=ascending, false=descending)
    - id: Filter by specific market ID(s)
    - slug: Filter by specific market slug(s)
    - archived: Filter by archived status
    - active: Filter by active status
    - closed: Filter by closed status
    - clob_token_ids: Filter by CLOB token ID(s)
    - condition_ids: Filter by condition ID(s)
    - liquidity_num_min: Filter by minimum liquidity
    - liquidity_num_max: Filter by maximum liquidity
    - volume_num_min: Filter by minimum volume
    - volume_num_max: Filter by maximum volume
    - start_date_min: Filter by minimum start date (ISO format)
    - start_date_max: Filter by maximum start date (ISO format)
    - end_date_min: Filter by minimum end date (ISO format)
    - end_date_max: Filter by maximum end date (ISO format)
    - tag_id: Filter by tag ID
    - related_tags: Include markets with related tags (requires tag_id)
    - status: (Deprecated) Filter by status string (open, closed, archived)
    """
    try:
        params = {}
        
        # Handle the legacy status parameter for backward compatibility
        if status:
            if status.lower() == "open":
                active = True
            elif status.lower() == "closed":
                closed = True
            elif status.lower() == "archived":
                archived = True
        
        # Add all parameters to the request
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if order:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = ascending
        if id is not None:
            # Handle both single value and list
            if isinstance(id, list):
                for single_id in id:
                    params.setdefault("id", []).append(single_id)
            else:
                params["id"] = id
        if slug is not None:
            # Handle both single value and list
            if isinstance(slug, list):
                for single_slug in slug:
                    params.setdefault("slug", []).append(single_slug)
            else:
                params["slug"] = slug
        if archived is not None:
            params["archived"] = archived
        if active is not None:
            params["active"] = active
        if closed is not None:
            params["closed"] = closed
        if clob_token_ids is not None:
            # Handle both single value and list
            if isinstance(clob_token_ids, list):
                for token_id in clob_token_ids:
                    params.setdefault("clob_token_ids", []).append(token_id)
            else:
                params["clob_token_ids"] = clob_token_ids
        if condition_ids is not None:
            # Handle both single value and list
            if isinstance(condition_ids, list):
                for condition_id in condition_ids:
                    params.setdefault("condition_ids", []).append(condition_id)
            else:
                params["condition_ids"] = condition_ids
        if liquidity_num_min is not None:
            params["liquidity_num_min"] = liquidity_num_min
        if liquidity_num_max is not None:
            params["liquidity_num_max"] = liquidity_num_max
        if volume_num_min is not None:
            params["volume_num_min"] = volume_num_min
        if volume_num_max is not None:
            params["volume_num_max"] = volume_num_max
        if start_date_min:
            params["start_date_min"] = start_date_min
        if start_date_max:
            params["start_date_max"] = start_date_max
        if end_date_min:
            params["end_date_min"] = end_date_min
        if end_date_max:
            params["end_date_max"] = end_date_max
        if tag_id is not None:
            params["tag_id"] = tag_id
        if related_tags is not None and tag_id is not None:
            params["related_tags"] = related_tags
        
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

@mcp.tool(description="[EXPERIMENTAL] Get the current order book for a specific market.")
async def get_order_book(market_id: str, outcome_id: Optional[str] = None) -> Dict[str, Any]:
    """
    [EXPERIMENTAL] Get the current order book for a market.
    
    Note: This endpoint may not be part of the official Gamma API documentation and may be subject
    to change without notice.
    
    Parameters:
    - market_id: The unique identifier of the market
    - outcome_id: Optional outcome ID to filter by
    """
    try:
        params = {}
        if outcome_id:
            params["outcome_id"] = outcome_id
            
        return await make_api_request(f"markets/{market_id}/orderbook", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting order book: {str(e)}\n")
        return {"error": str(e)}

@mcp.tool(description="[EXPERIMENTAL] Get the latest trades for a specific market.")
async def get_recent_trades(market_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    [EXPERIMENTAL] Get recent trades for a market.
    
    Note: This endpoint may not be part of the official Gamma API documentation and may be subject
    to change without notice.
    
    Parameters:
    - market_id: The unique identifier of the market
    - limit: Maximum number of trades to return
    """
    try:
        params = {"limit": limit}
        return await make_api_request(f"markets/{market_id}/trades", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting recent trades: {str(e)}\n")
        return {"trades": []}

@mcp.tool(description="[EXPERIMENTAL] Get historical market data for a specific market.")
async def get_market_history(market_id: str, resolution: str = "hour") -> Dict[str, Any]:
    """
    [EXPERIMENTAL] Get historical market data.
    
    Note: This endpoint may not be part of the official Gamma API documentation and may be subject
    to change without notice.
    
    Parameters:
    - market_id: The unique identifier of the market
    - resolution: Time resolution (hour, day, week)
    """
    try:
        params = {"resolution": resolution}
        return await make_api_request(f"markets/{market_id}/history", params=params)
    except Exception as e:
        sys.stderr.write(f"Error getting market history: {str(e)}\n")
        return {"history": []}

@mcp.tool(description="Search for markets by keyword or phrase using slug filtering.")
async def search_markets(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for markets by keyword using the slug parameter.
    
    Parameters:
    - query: Search term to match against market slugs
    - limit: Maximum number of results to return
    
    Note: This uses the general markets endpoint with slug filtering and is not
    a dedicated search API.
    """
    try:
        # Using the slug parameter for search
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

@mcp.tool(description="Get a list of all available events on Polymarket with comprehensive filtering options.")
async def get_events(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order: Optional[str] = None,
    ascending: Optional[bool] = None,
    id: Optional[Union[int, List[int]]] = None,
    slug: Optional[Union[str, List[str]]] = None,
    archived: Optional[bool] = None,
    active: Optional[bool] = None,
    closed: Optional[bool] = None,
    liquidity_min: Optional[float] = None,
    liquidity_max: Optional[float] = None,
    volume_min: Optional[float] = None,
    volume_max: Optional[float] = None,
    start_date_min: Optional[str] = None,
    start_date_max: Optional[str] = None,
    end_date_min: Optional[str] = None,
    end_date_max: Optional[str] = None,
    tag: Optional[str] = None,
    tag_id: Optional[int] = None,
    related_tags: Optional[bool] = None,
    tag_slug: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a list of all available events with extensive filtering options.
    
    Parameters:
    - limit: Maximum number of events to return
    - offset: Number of events to skip (for pagination)
    - order: Field to sort by
    - ascending: Sort direction (true=ascending, false=descending)
    - id: Filter by specific event ID(s)
    - slug: Filter by specific event slug(s)
    - archived: Filter by archived status
    - active: Filter by active status
    - closed: Filter by closed status
    - liquidity_min: Filter by minimum liquidity
    - liquidity_max: Filter by maximum liquidity
    - volume_min: Filter by minimum volume
    - volume_max: Filter by maximum volume
    - start_date_min: Filter by minimum start date (ISO format)
    - start_date_max: Filter by maximum start date (ISO format)
    - end_date_min: Filter by minimum end date (ISO format)
    - end_date_max: Filter by maximum end date (ISO format)
    - tag: Filter by tag labels (highest priority)
    - tag_id: Filter by tag ID (medium priority)
    - related_tags: Include events with related tags (requires tag_id)
    - tag_slug: Filter by tag slug (lowest priority)
    
    Note: The tag filters (tag, tag_id, tag_slug) are mutually exclusive with priority
    tag > tag_id > tag_slug.
    """
    try:
        params = {}
        
        # Add all parameters to the request
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if order:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = ascending
        if id is not None:
            # Handle both single value and list
            if isinstance(id, list):
                for single_id in id:
                    params.setdefault("id", []).append(single_id)
            else:
                params["id"] = id
        if slug is not None:
            # Handle both single value and list
            if isinstance(slug, list):
                for single_slug in slug:
                    params.setdefault("slug", []).append(single_slug)
            else:
                params["slug"] = slug
        if archived is not None:
            params["archived"] = archived
        if active is not None:
            params["active"] = active
        if closed is not None:
            params["closed"] = closed
        if liquidity_min is not None:
            params["liquidity_min"] = liquidity_min
        if liquidity_max is not None:
            params["liquidity_max"] = liquidity_max
        if volume_min is not None:
            params["volume_min"] = volume_min
        if volume_max is not None:
            params["volume_max"] = volume_max
        if start_date_min:
            params["start_date_min"] = start_date_min
        if start_date_max:
            params["start_date_max"] = start_date_max
        if end_date_min:
            params["end_date_min"] = end_date_min
        if end_date_max:
            params["end_date_max"] = end_date_max
        
        # Handle tag filter priority: tag > tag_id > tag_slug
        if tag:
            params["tag"] = tag
        elif tag_id is not None:
            params["tag_id"] = tag_id
            if related_tags is not None:
                params["related_tags"] = related_tags
        elif tag_slug:
            params["tag_slug"] = tag_slug
            
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
