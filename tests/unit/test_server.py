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
    get_order_book,
    create_order
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


@pytest.mark.asyncio
async def test_create_order_auth_error():
    """Test create_order when authentication is not available."""
    # Setup - ensure private key is not set
    with patch('polymarket_mcp_server.server.config') as mock_config:
        mock_config.use_authentication = True
        mock_config.private_key = ""
        
        # Call function and check exception
        with pytest.raises(ValueError, match="Authentication not available"):
            await create_order("market_id", "outcome_id", "BUY", "1.0", "0.5")


@pytest.mark.asyncio
async def test_create_order_validation_error():
    """Test create_order with invalid input parameters."""
    # Setup - ensure private key is set for this test
    with patch('polymarket_mcp_server.server.config') as mock_config, \
         patch('polymarket_mcp_server.server.make_request', new_callable=AsyncMock) as mock_make_request:
        mock_config.use_authentication = True
        mock_config.private_key = "test_key"
        
        # Test with invalid side
        with pytest.raises(ValueError, match="Side must be BUY or SELL"):
            await create_order("market_id", "outcome_id", "INVALID", "1.0", "0.5")
        
        # Test with invalid price
        with pytest.raises(ValueError, match="Price must be between 0 and 1"):
            await create_order("market_id", "outcome_id", "BUY", "1.0", "1.5")
        
        # Test with invalid size
        with pytest.raises(ValueError, match="Size must be positive"):
            await create_order("market_id", "outcome_id", "BUY", "-1.0", "0.5")

        # Ensure the mock was never called
        mock_make_request.assert_not_called()
