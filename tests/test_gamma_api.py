import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json
from polymarket_mcp_server.server import (
    get_markets,
    get_market_by_id,
    get_events,
    get_event_by_id,
    search_markets,
)

@pytest.fixture
def mock_make_api_request():
    with patch('polymarket_mcp_server.server.make_api_request') as mock:
        yield mock

@pytest.mark.asyncio
async def test_get_markets(mock_make_api_request):
    # Sample market data for testing
    sample_markets = {
        "markets": [
            {
                "id": 123,
                "slug": "sample-market",
                "liquidity_num": 50000.0,
                "volume_num": 25000.0,
                "active": True,
                "closed": False,
                "archived": False,
            }
        ]
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_markets
    
    # Call the function
    result = await get_markets()
    
    # Verify the API was called correctly
    mock_make_api_request.assert_called_once_with("markets", params={})
    
    # Verify the result is as expected
    assert result == sample_markets
    assert len(result["markets"]) == 1
    assert result["markets"][0]["id"] == 123

@pytest.mark.asyncio
async def test_get_markets_with_status(mock_make_api_request):
    # Sample market data for testing
    sample_markets = {
        "markets": [
            {
                "id": 123,
                "slug": "sample-market",
                "active": True,
                "closed": False,
                "archived": False,
            }
        ]
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_markets
    
    # Call the function with a status filter
    result = await get_markets(status="open")
    
    # Verify the API was called with the correct parameters
    mock_make_api_request.assert_called_once_with("markets", params={"active": True})
    
    # Verify the result is as expected
    assert result == sample_markets

@pytest.mark.asyncio
async def test_get_market_by_id(mock_make_api_request):
    # Sample market data for testing
    sample_market = {
        "id": 123,
        "slug": "sample-market",
        "liquidity_num": 50000.0,
        "volume_num": 25000.0,
        "active": True,
        "closed": False,
        "archived": False,
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_market
    
    # Call the function
    result = await get_market_by_id("123")
    
    # Verify the API was called correctly
    mock_make_api_request.assert_called_once_with("markets/123")
    
    # Verify the result is as expected
    assert result == sample_market
    assert result["id"] == 123

@pytest.mark.asyncio
async def test_get_events(mock_make_api_request):
    # Sample event data for testing
    sample_events = {
        "events": [
            {
                "id": 456,
                "slug": "sample-event",
                "markets": [
                    {"id": 123, "slug": "sample-market"}
                ],
                "active": True,
                "closed": False,
                "archived": False,
            }
        ]
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_events
    
    # Call the function
    result = await get_events(limit=10, active=True)
    
    # Verify the API was called correctly
    mock_make_api_request.assert_called_once_with("events", params={"limit": 10, "active": True})
    
    # Verify the result is as expected
    assert result == sample_events
    assert len(result["events"]) == 1
    assert result["events"][0]["id"] == 456

@pytest.mark.asyncio
async def test_search_markets(mock_make_api_request):
    # Sample market data for testing
    sample_markets = {
        "markets": [
            {
                "id": 123,
                "slug": "btc-price",
                "liquidity_num": 50000.0,
                "volume_num": 25000.0,
                "active": True,
                "closed": False,
                "archived": False,
            }
        ]
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_markets
    
    # Call the function
    result = await search_markets("bitcoin", limit=10)
    
    # Verify the API was called correctly
    mock_make_api_request.assert_called_once_with("markets", params={"slug": "bitcoin", "limit": 10})
    
    # Verify the result is as expected
    assert result == sample_markets
    assert len(result["markets"]) == 1
    assert result["markets"][0]["slug"] == "btc-price"

@pytest.mark.asyncio
async def test_get_event_by_id(mock_make_api_request):
    # Sample event data for testing
    sample_event = {
        "id": 456,
        "slug": "sample-event",
        "markets": [
            {"id": 123, "slug": "sample-market"}
        ],
        "active": True,
        "closed": False,
        "archived": False,
    }
    
    # Configure the mock to return the sample data
    mock_make_api_request.return_value = sample_event
    
    # Call the function
    result = await get_event_by_id("456")
    
    # Verify the API was called correctly
    mock_make_api_request.assert_called_once_with("events/456")
    
    # Verify the result is as expected
    assert result == sample_event
    assert result["id"] == 456

@pytest.mark.asyncio
async def test_api_error_handling(mock_make_api_request):
    # Simulate an API error
    mock_make_api_request.side_effect = Exception("API error")
    
    # Call the function and verify error handling
    result = await get_markets()
    
    # Verify the result contains an empty markets list
    assert result == {"markets": []}
