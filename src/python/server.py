#!/usr/bin/env python3
"""
Airtable MCP Server with HTTP/SSE Support for ChatGPT
---------------------------------------------------
This server provides HTTP/SSE endpoints for ChatGPT Custom Tools integration
while maintaining compatibility with existing MCP functionality.
"""
import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if FastMCP SDK is installed
try:
    from fastmcp import MCPServer
except ImportError:
    print("Error: FastMCP SDK not found. Please install with 'pip install fastmcp'")
    sys.exit(1)

# Import existing functionality
try:
    from airtable_mcp.src.server import (
        list_bases, list_tables, list_records, get_record,
        create_records, update_records, delete_records, set_base_id
    )
except ImportError:
    print("Error: Could not import existing MCP functions. Make sure airtable_mcp is properly installed.")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airtable-mcp-http")

# Create MCP server with HTTP/SSE support
server = MCPServer(
    name="Airtable MCP Server",
    description="Advanced Airtable MCP server with ChatGPT integration",
    version="3.2.5"
)

# Environment variables for ChatGPT integration
AIRTABLE_PAT = os.environ.get("AIRTABLE_PAT")
ALLOWED_BASES = os.environ.get("AIRTABLE_ALLOWED_BASES", "").split(",")
ALLOWED_TABLES = os.environ.get("AIRTABLE_ALLOWED_TABLES", "").split(",")

# Governance and Auth (placeholder - implement as needed)
class Governance:
    def validate_access(self, base: str, table: str, user: str) -> bool:
        """Validate access based on governance rules"""
        if ALLOWED_BASES and base not in ALLOWED_BASES:
            return False
        if ALLOWED_TABLES and table not in ALLOWED_TABLES:
            return False
        return True

class JWTVerifier:
    def verify(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token (placeholder implementation)"""
        # Implement JWT verification logic here
        return {"user": "authenticated_user"}

governance = Governance()
auth = JWTVerifier()

# HTTP endpoint for ChatGPT queries
@server.http_endpoint("/chatgpt_query")
async def chatgpt_query_endpoint(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ChatGPT queries via HTTP"""
    try:
        # Extract parameters from request
        prompt = request.get("prompt", "")
        base = request.get("base")
        table = request.get("table")
        user_token = request.get("user_token")

        # Authenticate user (if token provided)
        user_info = None
        if user_token:
            user_info = auth.verify(user_token)
            if not user_info:
                return {"error": "Invalid authentication token"}

        # Validate governance if base/table specified
        if base and table:
            if not governance.validate_access(base, table, user_info.get("user", "anonymous")):
                return {"error": "Access denied by governance rules"}

        # Process the query based on prompt content
        if "list tables" in prompt.lower():
            result = await list_tables()
        elif "list records" in prompt.lower() and table:
            result = await list_records(table)
        elif "get record" in prompt.lower() and table:
            record_id = prompt.split()[-1]  # Simple extraction
            result = await get_record(table, record_id)
        else:
            result = f"I can help you with Airtable operations. Available commands: list tables, list records [table], get record [table] [id]"

        return {
            "response": result,
            "status": "success",
            "timestamp": asyncio.get_event_loop().time()
        }

    except Exception as e:
        logger.error(f"ChatGPT query error: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        }

# Health check endpoint
@server.http_endpoint("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.2.5",
        "endpoints": ["/chatgpt_query", "/health"],
        "timestamp": asyncio.get_event_loop().time()
    }

# MCP tools (re-export existing tools for HTTP access)
@server.tool()
async def list_bases_tool() -> str:
    """List all accessible Airtable bases"""
    return await list_bases()

@server.tool()
async def list_tables_tool(base_id: Optional[str] = None) -> str:
    """List all tables in the specified base"""
    return await list_tables(base_id)

@server.tool()
async def list_records_tool(table_name: str, max_records: int = 100) -> str:
    """List records from a table"""
    return await list_records(table_name, max_records)

@server.tool()
async def get_record_tool(table_name: str, record_id: str) -> str:
    """Get a specific record from a table"""
    return await get_record(table_name, record_id)

@server.tool()
async def create_records_tool(table_name: str, records_json: str) -> str:
    """Create records in a table from JSON"""
    return await create_records(table_name, records_json)

@server.tool()
async def update_records_tool(table_name: str, records_json: str) -> str:
    """Update records in a table from JSON"""
    return await update_records(table_name, records_json)

@server.tool()
async def delete_records_tool(table_name: str, record_ids: str) -> str:
    """Delete records from a table"""
    return await delete_records(table_name, record_ids)

@server.tool()
async def set_base_id_tool(base_id: str) -> str:
    """Set the current Airtable base ID"""
    return await set_base_id(base_id)

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting Airtable MCP HTTP Server on {host}:{port}")
    logger.info("ChatGPT endpoint available at: /chatgpt_query")
    logger.info("Health check available at: /health")

    # Run the server with HTTP/SSE support
    server.run(host=host, port=port)