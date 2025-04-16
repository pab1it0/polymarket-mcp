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
    get_markets,
    get_market_by_id,
    search_markets,
    get_order_book
)


@pytest.fixture
def mock_make_request():
    """Fixture to mock the make_request function."""
    with patch('polymarket_mcp_server.server.make_request', new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_get_markets(mock_make_request):
    """Test the get_markets function."""
    # Setup mock
    mock_response = {"markets": [{"id": "123", "name": "Test Market"}]}
    mock_make_request.return_value = mock_response
    
    # Call function
    result = await get_markets()
    
    # Assertions
    mock_make_request.assert_called_once_with("/markets", params={})
    assert result == [{"id": "123", "name": "Test Market"}]


@pytest.mark.asyncio
async def test_get_markets_with_status(mock_make_request):
    """Test the get_markets function with status filter."""
    # Setup mock
    mock_response = {"markets": [{"id": "123", "name": "Test Market", "status": "OPEN"}]}
    mock_make_request.return_value = mock_response
    
    # Call function
    result = await get_markets(status="OPEN")
    
    # Assertions
    mock_make_request.assert_called_once_with("/markets", params={"status": "OPEN"})
    assert result == [{"id": "123", "name": "Test Market", "status": "OPEN"}]


@pytest.mark.asyncio
async def test_get_market_by_id(mock_make_request):
    """Test the get_market_by_id function."""
    # Setup mock
    market_id = "market_123"
    mock_response = {"id": market_id, "name": "Test Market", "description": "Test Description"}
    mock_make_request.return_value = mock_response
    
    # Call function
    result = await get_market_by_id(market_id)
    
    # Assertions
    mock_make_request.assert_called_once_with(f"/markets/{market_id}")
    assert result == mock_response


@pytest.mark.asyncio
async def test_search_markets(mock_make_request):
    """Test the search_markets function."""
    # Setup mock
    query = "election"
    mock_response = {"markets": [{"id": "123", "name": "Election Market"}]}
    mock_make_request.return_value = mock_response
    
    # Call function
    result = await search_markets(query)
    
    # Assertions
    mock_make_request.assert_called_once_with("/markets/search", params={"q": query, "limit": 20})
    assert result == [{"id": "123", "name": "Election Market"}]


@pytest.mark.asyncio
async def test_get_order_book(mock_make_request):
    """Test the get_order_book function."""
    # Setup mock
    market_id = "market_123"
    mock_response = {"bids": [], "asks": []}
    mock_make_request.return_value = mock_response
    
    # Call function
    result = await get_order_book(market_id)
    
    # Assertions
    mock_make_request.assert_called_once_with("/orderbook", params={"marketId": market_id})
    assert result == mock_response
