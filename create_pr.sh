#!/bin/bash
# Script to help create a PR for the MCP JSON communication fix

# Ensure we're in the correct branch
git checkout fix/mcp-json-communication

# Instructions for creating the PR
echo "To create a pull request for the MCP JSON communication fix:"
echo ""
echo "1. Push the branch to GitHub:"
echo "   git push origin fix/mcp-json-communication"
echo ""
echo "2. Go to your GitHub repository and create a PR:"
echo "   - Base: main"
echo "   - Compare: fix/mcp-json-communication"
echo ""
echo "3. Use the content from PR_DESCRIPTION.md as the PR description"
echo ""
echo "4. Submit the pull request"
