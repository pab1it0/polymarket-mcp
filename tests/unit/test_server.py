#!/usr/bin/env python
"""
Unit tests for the Polymarket MCP server.
"""

import os
import json
import pytest
import httpx
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
    # Set up mock response - Gamma API returns a list
    mock_response = [{"id": "123", "name": "Test Market"}]
    mock_make_api_request.return_value = mock_response

    # Execute the function
    result = await get_markets()

    # Verify the call arguments
    mock_make_api_request.assert_called_once_with("markets", params={})

    # Verify the result is wrapped in a dict
    assert result == {"markets": [{"id": "123", "name": "Test Market"}]}


@pytest.mark.asyncio
async def test_get_markets_with_status(mock_make_api_request):
    """Test the get_markets function with status filter."""
    mock_response = [{"id": "123", "name": "Test Market", "active": True}]
    mock_make_api_request.return_value = mock_response

    # Execute with status="open" which maps to active=True
    result = await get_markets(status="open")

    # Verify active param is set from status
    mock_make_api_request.assert_called_once_with("markets", params={"active": True})

    assert result == {"markets": [{"id": "123", "name": "Test Market", "active": True}]}


@pytest.mark.asyncio
async def test_get_market_by_id(mock_make_api_request):
    """Test the get_market_by_id function."""
    market_id = "market_123"

    mock_response = {"id": market_id, "name": "Test Market", "description": "Test Description"}
    mock_make_api_request.return_value = mock_response

    result = await get_market_by_id(market_id)

    mock_make_api_request.assert_called_once_with(f"markets/{market_id}")
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_markets(mock_make_api_request):
    """Test the search_markets function."""
    query = "election"

    mock_response = [{"id": "123", "name": "Election Market"}]
    mock_make_api_request.return_value = mock_response

    result = await search_markets(query)

    mock_make_api_request.assert_called_once_with("markets", params={"slug": query, "limit": 20})

    assert result == {"markets": [{"id": "123", "name": "Election Market"}]}


@pytest.mark.asyncio
async def test_get_order_book(mock_make_api_request):
    """Test the get_order_book function."""
    market_id = "market_123"

    mock_response = {"bids": [], "asks": []}
    mock_make_api_request.return_value = mock_response

    result = await get_order_book(market_id)

    mock_make_api_request.assert_called_once_with(f"markets/{market_id}/orderbook", params={})
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_order_book_with_outcome(mock_make_api_request):
    """Test the get_order_book function with outcome filter."""
    market_id = "market_123"
    outcome_id = "outcome_456"

    mock_response = {"bids": [{"price": "0.5", "size": "100"}], "asks": []}
    mock_make_api_request.return_value = mock_response

    result = await get_order_book(market_id, outcome_id)

    mock_make_api_request.assert_called_once_with(
        f"markets/{market_id}/orderbook", params={"outcome_id": outcome_id}
    )
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_recent_trades(mock_make_api_request):
    """Test the get_recent_trades function."""
    market_id = "market_123"

    mock_response = [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]
    mock_make_api_request.return_value = mock_response

    result = await get_recent_trades(market_id)

    mock_make_api_request.assert_called_once_with(
        f"markets/{market_id}/trades", params={"limit": 50}
    )
    assert result == {"trades": [{"price": "0.75", "size": "50", "timestamp": "2025-04-17T12:00:00Z"}]}


@pytest.mark.asyncio
async def test_get_recent_trades_with_limit(mock_make_api_request):
    """Test the get_recent_trades function with custom limit."""
    market_id = "market_123"
    limit = 25

    mock_response = [{"price": "0.75", "size": "50"}]
    mock_make_api_request.return_value = mock_response

    result = await get_recent_trades(market_id, limit)

    mock_make_api_request.assert_called_once_with(
        f"markets/{market_id}/trades", params={"limit": limit}
    )
    assert result == {"trades": [{"price": "0.75", "size": "50"}]}


@pytest.mark.asyncio
async def test_get_market_history(mock_make_api_request):
    """Test the get_market_history function."""
    market_id = "market_123"

    mock_response = [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]
    mock_make_api_request.return_value = mock_response

    result = await get_market_history(market_id)

    mock_make_api_request.assert_called_once_with(
        f"markets/{market_id}/history", params={"resolution": "hour"}
    )
    assert result == {"history": [{"timestamp": "2025-04-17T00:00:00Z", "price": "0.65", "volume": "1000"}]}


@pytest.mark.asyncio
async def test_get_market_history_with_resolution(mock_make_api_request):
    """Test the get_market_history function with custom resolution."""
    market_id = "market_123"
    resolution = "day"

    mock_response = [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]
    mock_make_api_request.return_value = mock_response

    result = await get_market_history(market_id, resolution)

    mock_make_api_request.assert_called_once_with(
        f"markets/{market_id}/history", params={"resolution": resolution}
    )
    assert result == {"history": [{"timestamp": "2025-04-17", "price": "0.65", "volume": "5000"}]}


@pytest.mark.asyncio
async def test_get_markets_dict_response(mock_make_api_request):
    """Test that get_markets passes through dict responses unchanged."""
    mock_response = {"markets": [{"id": "123"}], "next_cursor": "abc"}
    mock_make_api_request.return_value = mock_response

    result = await get_markets()
    assert result == mock_response


@pytest.mark.asyncio
async def test_make_api_request_get():
    """Test the make_api_request function with GET method."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_client.get.return_value = mock_response

    with patch('httpx.AsyncClient') as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None

        endpoint = "test"
        params = {"param1": "value1"}
        result = await make_api_request(endpoint, params=params)

        assert result == {"data": "test"}

        url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == url
        assert "params" in kwargs
        assert kwargs["params"] == params


@pytest.mark.asyncio
async def test_make_api_request_error_handling():
    """Test that make_api_request handles errors correctly."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )
    mock_client.get.return_value = mock_response

    with patch('httpx.AsyncClient') as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client
        mock_async_client.return_value.__aexit__.return_value = None

        with pytest.raises(httpx.HTTPStatusError):
            await make_api_request("test")

        mock_client.get.assert_called_once()
