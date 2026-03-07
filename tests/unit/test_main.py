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
        with patch('polymarket_mcp_server.main.load_dotenv', return_value=True):
            original_api_url = config.api_url

            try:
                config.api_url = "https://test-gamma.polymarket.com"

                result = main.setup_environment()

                assert result is True
            finally:
                config.api_url = original_api_url

    def test_setup_environment_without_env_file(self):
        """Test setup_environment when .env loading raises."""
        with patch('polymarket_mcp_server.main.load_dotenv', side_effect=Exception("no .env")):
            original_api_url = config.api_url

            try:
                config.api_url = "https://test-gamma.polymarket.com"

                result = main.setup_environment()

                assert result is True
            finally:
                config.api_url = original_api_url

    def test_run_server_successful(self):
        """Test run_server when setup is successful."""
        with patch('polymarket_mcp_server.main.setup_environment', return_value=True), \
             patch('polymarket_mcp_server.main.mcp.run') as mock_run, \
             patch('sys.stderr'):

            main.run_server()

            mock_run.assert_called_once_with(transport="stdio")

    def test_run_server_failed_setup(self):
        """Test run_server when setup fails."""
        with patch('polymarket_mcp_server.main.setup_environment', return_value=False), \
             patch('polymarket_mcp_server.main.sys.exit') as mock_exit, \
             patch('polymarket_mcp_server.main.mcp.run'), \
             patch('sys.stderr'):

            main.run_server()

            mock_exit.assert_called_once_with(1)
