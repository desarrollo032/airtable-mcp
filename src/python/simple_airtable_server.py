#!/usr/bin/env python3
"""
Simple Airtable MCP Server for Claude
-------------------------------------
A minimal MCP server that implements Airtable tools and Claude's special methods
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

# Async HTTP client
try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run 'pip install httpx'")
    sys.exit(1)

# Check if MCP SDK is installed
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP SDK not found. Please install with 'pip install mcp'")
    sys.exit(1)

# Load token and base ID from environment or CLI
token = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")

for i in range(1, len(sys.argv)):
    if sys.argv[i] == "--token" and i + 1 < len(sys.argv):
        token = sys.argv[i + 1]
    elif sys.argv[i] == "--base" and i + 1 < len(sys.argv):
        base_id = sys.argv[i + 1]

if not token or not base_id:
    print("Error: Provide Airtable token and base ID via ENV or CLI")
    sys.exit(1)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airtable-mcp")

# Create MCP server
app = FastMCP("Airtable Tools")

# -------------------------------
# Helper function: async Airtable API call
# -------------------------------
async def airtable_api_call(endpoint: str, method: str = "GET", data: Optional[Any] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://api.airtable.com/v0/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(method.upper(), url, headers=headers, json=data, params=params)
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"raw": resp.text}
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
            except Exception:
                body = {"status_code": e.response.status_code, "text": e.response.text}
            return {"error": f"API status error: {body}"}
        except Exception as e:
            return {"error": str(e)}

# -------------------------------
# Claude-specific RPC methods
# -------------------------------
@app.rpc_method("resources/list")
async def resources_list(params: Dict = None) -> Dict:
    try:
        resources = [
            {"id": "airtable_tables", "name": "Airtable Tables", "description": "Tables in your Airtable base"}
        ]
        return {"resources": resources}
    except Exception as e:
        logger.error(f"Error in resources/list: {e}")
        return {"error": {"code": -32000, "message": str(e)}}

@app.rpc_method("prompts/list")
async def prompts_list(params: Dict = None) -> Dict:
    try:
        prompts = [
            {"id": "tables_prompt", "name": "List Tables", "description": "List all tables"}
        ]
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Error in prompts/list: {e}")
        return {"error": {"code": -32000, "message": str(e)}}

# -------------------------------
# Airtable Tool Functions
# -------------------------------
@app.tool()
async def list_tables() -> str:
    result = await airtable_api_call(f"meta/bases/{quote_plus(base_id)}/tables")
    if "error" in result:
        return f"Error: {result['error']}"
    tables = result.get("tables", [])
    if not tables:
        return "No tables found in this base."
    return "\n".join([f"{i+1}. {t['name']} (ID: {t['id']})" for i, t in enumerate(tables)])

@app.tool()
async def list_records(table_name: str, max_records: int = 100) -> str:
    endpoint = f"{quote_plus(base_id)}/{quote_plus(table_name)}"
    params = {"maxRecords": max_records}
    result = await airtable_api_call(endpoint, params=params)
    if "error" in result:
        return f"Error: {result['error']}"
    records = result.get("records", [])
    if not records:
        return "No records found in this table."
    lines = []
    for i, r in enumerate(records, start=1):
        fields = r.get("fields", {})
        lines.append(f"{i}. ID: {r.get('id', 'unknown')} - {fields}")
    return "\n".join(lines)

@app.tool()
async def set_base_id(new_base_id: str) -> str:
    global base_id
    base_id = new_base_id
    return f"Base ID set to {new_base_id}"

# -------------------------------
# Server entrypoint
# -------------------------------
if __name__ == "__main__":
    logger.info(f"Starting Airtable MCP Server on base {base_id}")
    app.run()
