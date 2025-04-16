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

# Optional: Import py-clob-client when authentication is needed
try:
    from py_clob_client.client import ClobClient
    CLOB_CLIENT_AVAILABLE = True
except ImportError:
    CLOB_CLIENT_AVAILABLE = False
    print("WARNING: py-clob-client not available. Authentication for private endpoints will not work.")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
mcp = FastMCP("Polymarket MCP")

@dataclass
class PolymarketConfig:
    api_url: str
    chain_id: int
    private_key: Optional[str]
    use_authentication: bool

# Load configuration from environment variables with defaults
config = PolymarketConfig(
    api_url=os.environ.get("POLYMARKET_API_URL", "https://clob.polymarket.com"),
    chain_id=int(os.environ.get("POLYMARKET_CHAIN_ID", "137")),  # Default to Polygon mainnet
    private_key=os.environ.get("POLYMARKET_PRIVATE_KEY", ""),
    use_authentication=os.environ.get("POLYMARKET_USE_AUTH", "true").lower() in ("true", "1", "yes"),
)

# Cache for API credentials to avoid recreating them
_api_creds_cache = None

def get_api_credentials():
    """Get API credentials for authenticated requests."""
    global _api_creds_cache
    
    if _api_creds_cache:
        return _api_creds_cache
    
    if not config.private_key or not CLOB_CLIENT_AVAILABLE:
        raise ValueError("Private key not configured or py-clob-client not available")
    
    try:
        client = ClobClient(config.api_url, key=config.private_key, chain_id=config.chain_id)
        api_creds = client.create_or_derive_api_creds()
        _api_creds_cache = api_creds
        return api_creds
    except Exception as e:
        logger.error(f"Failed to create API credentials: {e}")
        raise

def create_auth_headers():
    """Create authentication headers for Polymarket API requests."""
    if not config.use_authentication or not config.private_key:
        return {}
    
    try:
        api_creds = get_api_credentials()
        return {
            "POLY_ADDRESS": api_creds.address,
            "POLY_SIGNATURE": api_creds.signature,
            "POLY_TIMESTAMP": str(api_creds.timestamp),
            "POLY_API_KEY": api_creds.api_key,
            "POLY_PASSPHRASE": api_creds.api_passphrase,
        }
    except Exception as e:
        logger.warning(f"Could not create authentication headers: {e}")
        return {}

async def make_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None, auth_required: bool = False) -> Dict[str, Any]:
    """Make a request to the Polymarket API."""
    url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and config.use_authentication:
        try:
            auth_headers = create_auth_headers()
            headers.update(auth_headers)
        except Exception as e:
            logger.warning(f"Authentication failed, proceeding without authentication: {e}")
    
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

@mcp.tool(description="Get user account information (requires authentication).")
async def get_account_info() -> Dict[str, Any]:
    """
    Get user account information.
    
    Returns:
        Account details including balances
    """
    if not config.use_authentication or not config.private_key:
        raise ValueError("Authentication not available. Set POLYMARKET_PRIVATE_KEY environment variable.")
    
    response = await make_request("/account", auth_required=True)
    return response

@mcp.tool(description="Get a user's orders (requires authentication).")
async def get_user_orders(status: Optional[str] = None, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get a user's orders.
    
    Args:
        status: Filter by order status (OPEN, FILLED, CANCELLED)
        market_id: Filter by market ID
    
    Returns:
        List of user orders
    """
    if not config.use_authentication or not config.private_key:
        raise ValueError("Authentication not available. Set POLYMARKET_PRIVATE_KEY environment variable.")
    
    params = {}
    if status:
        params["status"] = status
    if market_id:
        params["marketId"] = market_id
    
    response = await make_request("/orders", params=params, auth_required=True)
    return response.get("orders", [])

@mcp.tool(description="Create a new order to buy or sell shares in a market (requires authentication).")
async def create_order(
    market_id: str,
    outcome_id: str,
    side: str,  # BUY or SELL
    size: str,  # Amount to buy/sell
    price: str,  # Price in range 0-1
) -> Dict[str, Any]:
    """
    Create a new order.
    
    Args:
        market_id: The unique identifier of the market
        outcome_id: The outcome ID to trade
        side: Order side (BUY or SELL)
        size: Order size
        price: Order price (0-1)
    
    Returns:
        Order details
    """
    if not config.use_authentication or not config.private_key:
        raise ValueError("Authentication not available. Set POLYMARKET_PRIVATE_KEY environment variable.")
    
    # Validate inputs
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")
    
    try:
        price_float = float(price)
        if not 0 <= price_float <= 1:
            raise ValueError("Price must be between 0 and 1")
    except ValueError:
        raise ValueError("Invalid price format")
    
    try:
        size_float = float(size)
        if size_float <= 0:
            raise ValueError("Size must be positive")
    except ValueError:
        raise ValueError("Invalid size format")
    
    data = {
        "marketId": market_id,
        "outcomeId": outcome_id,
        "side": side,
        "size": size,
        "price": price,
    }
    
    response = await make_request("/orders", method="POST", data=data, auth_required=True)
    return response

@mcp.tool(description="Cancel an existing order (requires authentication).")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancel an order.
    
    Args:
        order_id: The ID of the order to cancel
    
    Returns:
        Cancellation result
    """
    if not config.use_authentication or not config.private_key:
        raise ValueError("Authentication not available. Set POLYMARKET_PRIVATE_KEY environment variable.")
    
    data = {"orderId": order_id}
    response = await make_request("/orders/cancel", method="POST", data=data, auth_required=True)
    return response

@mcp.tool(description="Get portfolio positions for the authenticated user (requires authentication).")
async def get_portfolio() -> List[Dict[str, Any]]:
    """
    Get user portfolio positions.
    
    Returns:
        List of portfolio positions
    """
    if not config.use_authentication or not config.private_key:
        raise ValueError("Authentication not available. Set POLYMARKET_PRIVATE_KEY environment variable.")
    
    response = await make_request("/portfolio", auth_required=True)
    return response.get("positions", [])

if __name__ == "__main__":
    print(f"Starting Polymarket MCP Server...")
    mcp.run()
