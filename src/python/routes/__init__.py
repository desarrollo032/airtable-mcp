"""
Routes module for Airtable MCP Server.
Provides HTTP endpoints for authentication and MCP operations.
"""
from .auth import auth_routes
from .mcp import mcp_routes

__all__ = ["auth_routes", "mcp_routes"]
