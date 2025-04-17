#!/usr/bin/env python
"""
Unit tests for the Polymarket MCP main module.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from polymarket_mcp_server import main
from polymarket_mcp_server.server import config


class TestMain:
    def test_setup_environment_with_env_file(self):
        """Test setup_environment when .env file is found."""
        with patch('polymarket_mcp_server.main.dotenv.load_dotenv', return_value=True), \
             patch('polymarket_mcp_server.main.print') as mock_print:
            
            # Set some test values
            original_api_url = config.api_url
            original_chain_id = config.chain_id
            
            try:
                config.api_url = "https://test.polymarket.com"
                config.chain_id = 999
                
                result = main.setup_environment()
                
                # Verify that the function returns True
                assert result is True
                
                # Verify the print statements
                mock_print.assert_any_call("Loaded environment variables from .env file")
                mock_print.assert_any_call("Polymarket API configuration:")
                mock_print.assert_any_call(f"  API URL: {config.api_url}")
                mock_print.assert_any_call(f"  Chain ID: {config.chain_id}")
            finally:
                # Restore original values
                config.api_url = original_api_url
                config.chain_id = original_chain_id
    
    def test_setup_environment_without_env_file(self):
        """Test setup_environment when .env file is not found."""
        with patch('polymarket_mcp_server.main.dotenv.load_dotenv', return_value=False), \
             patch('polymarket_mcp_server.main.print') as mock_print:
            
            # Set some test values
            original_api_url = config.api_url
            original_chain_id = config.chain_id
            
            try:
                config.api_url = "https://test.polymarket.com"
                config.chain_id = 999
                
                result = main.setup_environment()
                
                # Verify that the function returns True
                assert result is True
                
                # Verify the print statements
                mock_print.assert_any_call("No .env file found or could not load it - using environment variables")
                mock_print.assert_any_call("Polymarket API configuration:")
                mock_print.assert_any_call(f"  API URL: {config.api_url}")
                mock_print.assert_any_call(f"  Chain ID: {config.chain_id}")
            finally:
                # Restore original values
                config.api_url = original_api_url
                config.chain_id = original_chain_id
    
    def test_setup_environment_missing_api_url(self):
        """Test setup_environment when API URL is missing."""
        with patch('polymarket_mcp_server.main.dotenv.load_dotenv', return_value=True), \
             patch('polymarket_mcp_server.main.print') as mock_print:
            
            # Set some test values
            original_api_url = config.api_url
            
            try:
                config.api_url = ""
                
                result = main.setup_environment()
                
                # Verify that the function returns True (since API URL is optional)
                assert result is True
                
                # Verify the warning print statements
                mock_print.assert_any_call("WARNING: POLYMARKET_API_URL environment variable is not set")
                mock_print.assert_any_call("Using default API URL: https://clob.polymarket.com")
            finally:
                # Restore original values
                config.api_url = original_api_url
    
    def test_run_server_successful(self):
        """Test run_server when setup is successful."""
        with patch('polymarket_mcp_server.main.setup_environment', return_value=True), \
             patch('polymarket_mcp_server.main.mcp.run') as mock_run, \
             patch('polymarket_mcp_server.main.print'):
            
            main.run_server()
            
            # Verify that mcp.run was called with correct arguments
            mock_run.assert_called_once_with(transport="stdio")
    
    def test_run_server_failed_setup(self):
        """Test run_server when setup fails."""
        with patch('polymarket_mcp_server.main.setup_environment', return_value=False), \
             patch('polymarket_mcp_server.main.sys.exit') as mock_exit, \
             patch('polymarket_mcp_server.main.print'):
            
            main.run_server()
            
            # Verify that sys.exit was called with the correct error code
            mock_exit.assert_called_once_with(1)
