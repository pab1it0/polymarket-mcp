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
    make_request,
    get_markets,
    get_market_by_id,
    search_markets,
    get_order_book,
    get_recent_trades,
    get_market_history
)


@pytest.fixture
def mock_make_request():
    """Fixture to mock the make_request function."""
    with patch('polymarket_mcp_server.server.make_request', new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_get_markets(mock_make_request):
    """Test the get_markets function."""
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Test Market"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_markets()
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/markets", params={})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Test Market"}]


@pytest.mark.asyncio
async def test_get_markets_with_status(mock_make_request):
    """Test the get_markets function with status filter."""
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Test Market", "status": "OPEN"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_markets(status="OPEN")
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/markets", params={"status": "OPEN"})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Test Market", "status": "OPEN"}]


@pytest.mark.asyncio
async def test_get_market_by_id(mock_make_request):
    """Test the get_market_by_id function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"id": market_id, "name": "Test Market", "description": "Test Description"}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_by_id(market_id)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with(f"/markets/{market_id}")
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_markets(mock_make_request):
    """Test the search_markets function."""
    # Set up test parameters
    query = "election"
    
    # Set up mock response
    mock_response = {"markets": [{"id": "123", "name": "Election Market"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await search_markets(query)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/markets/search", params={"q": query, "limit": 20})
    
    # Verify the result
    assert result == [{"id": "123", "name": "Election Market"}]


@pytest.mark.asyncio
async def test_get_order_book(mock_make_request):
    """Test the get_order_book function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"bids": [], "asks": []}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_order_book(market_id)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/orderbook", params={"marketId": market_id})
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_order_book_with_outcome(mock_make_request):
    """Test the get_order_book function with outcome filter."""
    # Set up test parameters
    market_id = "market_123"
    outcome_id = "outcome_456"
    
    # Set up mock response
    mock_response = {"bids": [{"price": "0.5", "size": "100"}], "asks": []}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_order_book(market_id, outcome_id)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/orderbook", params={"marketId": market_id, "outcomeId": outcome_id})
    
    # Verify the result
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_recent_trades(mock_make_request):
    """Test the get_recent_trades function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"trades": [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_recent_trades(market_id)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/trades", params={"marketId": market_id, "limit": 50})
    
    # Verify the result
    assert result == [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]


@pytest.mark.asyncio
async def test_get_recent_trades_with_limit(mock_make_request):
    """Test the get_recent_trades function with custom limit."""
    # Set up test parameters
    market_id = "market_123"
    limit = 25
    
    # Set up mock response
    mock_response = {"trades": [{"price": "0.75", "size": "50"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_recent_trades(market_id, limit)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/trades", params={"marketId": market_id, "limit": limit})
    
    # Verify the result
    assert result == [{"price": "0.75", "size": "50"}]


@pytest.mark.asyncio
async def test_get_market_history(mock_make_request):
    """Test the get_market_history function."""
    # Set up test parameters
    market_id = "market_123"
    
    # Set up mock response
    mock_response = {"history": [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_history(market_id)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/markets/history", params={"marketId": market_id, "resolution": "hour"})
    
    # Verify the result
    assert result == [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]


@pytest.mark.asyncio
async def test_get_market_history_with_resolution(mock_make_request):
    """Test the get_market_history function with custom resolution."""
    # Set up test parameters
    market_id = "market_123"
    resolution = "day"
    
    # Set up mock response
    mock_response = {"history": [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]}
    mock_make_request.return_value = mock_response
    
    # Execute the function
    result = await get_market_history(market_id, resolution)
    
    # Verify the call arguments
    mock_make_request.assert_called_once_with("/markets/history", params={"marketId": market_id, "resolution": resolution})
    
    # Verify the result
    assert result == [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]


@pytest.mark.asyncio
async def test_make_request_get(monkeypatch):
    """Test the make_request function with GET method."""
    # Mock aiohttp.ClientSession
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})
    mock_session.get = AsyncMock(return_value=mock_response)
    
    # Create mock context manager for aiohttp.ClientSession
    class MockClientSession:
        async def __aenter__(self):
            return mock_session
        
        async def __aexit__(self, *args):
            pass
    
    # Patch aiohttp.ClientSession
    with patch('polymarket_mcp_server.server.aiohttp.ClientSession', return_value=MockClientSession()):
        endpoint = "/test"
        params = {"param1": "value1"}
        result = await make_request(endpoint, params=params)
        
        # Verify result
        assert result == {"data": "test"}
        
        # Verify ClientSession.get was called with correct parameters
        url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        mock_session.get.assert_called_once()
        args, kwargs = mock_session.get.call_args
        assert args[0] == url
        assert "params" in kwargs
        assert kwargs["params"] == params


@pytest.mark.asyncio
async def test_make_request_error_handling(monkeypatch):
    """Test that make_request handles errors correctly."""
    # Mock aiohttp.ClientSession
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.text = AsyncMock(return_value="Not Found")
    mock_session.get = AsyncMock(return_value=mock_response)
    
    # Create mock context manager for aiohttp.ClientSession
    class MockClientSession:
        async def __aenter__(self):
            return mock_session
        
        async def __aexit__(self, *args):
            pass
    
    # Patch aiohttp.ClientSession and print function
    with patch('polymarket_mcp_server.server.aiohttp.ClientSession', return_value=MockClientSession()), \
         patch('polymarket_mcp_server.server.print') as mock_print:
        
        endpoint = "/test"
        
        # Test that ValueError is raised for non-200 status
        with pytest.raises(ValueError) as excinfo:
            await make_request(endpoint)
        
        assert "Request failed with status 404" in str(excinfo.value)
        
        # Verify ClientSession.get was called
        mock_session.get.assert_called_once()
