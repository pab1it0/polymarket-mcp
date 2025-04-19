#!/usr/bin/env python
"""
Unit tests for the Polymarket MCP server.
"""

import os
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from polymarket_mcp_server.server import (
    mcp,
    config,
    make_api_request,
    get_markets,
    get_market_by_id,
    search_markets,
    get_order_book,
    get_recent_trades,
    get_market_history
)


@pytest.fixture
def mock_make_api_request():
    """Fixture to mock the make_api_request function."""
    with patch('polymarket_mcp_server.server.make_api_request', new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_get_markets(mock_make_api_request):
    """Test the get_markets function."""
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Test Market"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_markets()
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets", params={})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Test Market"}]


@pytest.mark.asyncio
async def test_get_markets_with_status(mock_make_api_request):
    """Test the get_markets function with status filter."""
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Test Market", "status": "OPEN"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_markets(status="OPEN")
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets", params={"status": "OPEN"})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Test Market", "status": "OPEN"}]


@pytest.mark.asyncio
async def test_get_market_by_id(mock_make_api_request):
    """Test the get_market_by_id function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"id": market_id, "name": "Test Market", "description": "Test Description"}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_by_id(market_id)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with(f"markets/{market_id}")
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_markets(mock_make_api_request):
    """Test the search_markets function."""
    # Set up test parameters
    query = "election"
    
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Election Market"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await search_markets(query)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets/search", params={"q": query, "limit": 20})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Election Market"}]


@pytest.mark.asyncio
async def test_get_order_book(mock_make_api_request):
    """Test the get_order_book function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"bids": [], "asks": []}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_order_book(market_id)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("orderbook", params={"marketId": market_id})
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_order_book_with_outcome(mock_make_api_request):
    """Test the get_order_book function with outcome filter."""
    # Set up test parameters
    market_id = "market_123"
    outcome_id = "outcome_456"
    
    # Set up mock response
    mock_response = {"bids": [{"price": "0.5", "size": "100"}], "asks": []}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_order_book(market_id, outcome_id)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("orderbook", params={"marketId": market_id, "outcomeId": outcome_id})
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_recent_trades(mock_make_api_request):
    """Test the get_recent_trades function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"trades": [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_recent_trades(market_id)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("trades", params={"marketId": market_id, "limit": 50})
    
    # Verify the result
    assert result == [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]


@pytest.mark.asyncio
async def test_get_recent_trades_with_limit(mock_make_api_request):
    """Test the get_recent_trades function with custom limit."""
    # Set up test parameters
    market_id = "market_123"
    limit = 25
    
    # Set up mock response
    mock_response = {"trades": [{"price": "0.75", "size": "50"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_recent_trades(market_id, limit)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("trades", params={"marketId": market_id, "limit": limit})
    
    # Verify the result
    assert result == [{"price": "0.75", "size": "50"}]


@pytest.mark.asyncio
async def test_get_market_history(mock_make_api_request):
    """Test the get_market_history function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"history": [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_history(market_id)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets/history", params={"marketId": market_id, "resolution": "hour"})
    
    # Verify the result
    assert result == [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]


@pytest.mark.asyncio
async def test_get_market_history_with_resolution(mock_make_api_request):
    """Test the get_market_history function with custom resolution."""
    # Set up test parameters
    market_id = "market_123"
    resolution = "day"
    
    # Set up mock response
    mock_response = {"history": [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]}
    mock_make_api_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_history(market_id, resolution)
    
    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets/history", params={"marketId": market_id, "resolution": resolution})
    
    # Verify the result
    assert result == [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]


@pytest.mark.asyncio
async def test_make_api_request_get():
    """Test the make_api_request function with GET method."""
    # Mock httpx.AsyncClient
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_client.get.return_value = mock_response
    
    # Patch httpx.AsyncClient
    with patch('httpx.AsyncClient') as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None
        
        # Call function
        endpoint = "test"
        params = {"param1": "value1"}
        result = await make_api_request(endpoint, params=params)
        
        # Verify result
        assert result == {"data": "test"}
        
        # Verify method calls
        url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == url
        assert "params" in kwargs
        assert kwargs["params"] == params


@pytest.mark.asyncio
async def test_make_api_request_error_handling():
    """Test that make_api_request handles errors correctly."""
    # Mock httpx.AsyncClient
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )
    mock_client.get.return_value = mock_response
    
    # Patch httpx.AsyncClient
    with patch('httpx.AsyncClient') as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None
        
        # Test that HTTPStatusError is raised
        with pytest.raises(httpx.HTTPStatusError):
            await make_api_request("test")
        
        # Verify method was called
        mock_client.get.assert_called_once()
