#!/usr/bin/env python3
"""
Airtable MCP Inspector Server
-----------------------------
A simple MCP server that implements the Airtable tools
"""

import os
import sys
import json
import logging
import requests
import argparse
import traceback
from requests import exceptions as requests_exceptions
from typing import Optional

# Import MCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP SDK not found. Please install with 'pip install mcp'")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airtable-mcp")

# Timeout
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("AIRTABLE_REQUEST_TIMEOUT", "30"))

# Command-line args
def parse_args():
    parser = argparse.ArgumentParser(description="Airtable MCP Server")
    parser.add_argument("--token", dest="api_token", help="Airtable Personal Access Token")
    parser.add_argument("--base", dest="base_id", help="Airtable Base ID")
    parser.add_argument("--config", dest="config_json", help="Configuration as JSON (for Smithery integration)")
    parser.add_argument("--host", dest="host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", dest="port", type=int, default=8000, help="Port to bind the server to")
    return parser.parse_args()

args = parse_args()

# Load config JSON if provided
config = {}
if args.config_json:
    try:
        config_str = args.config_json.rstrip('\\"').strip()
        if config_str.startswith('"') and config_str.endswith('"'):
            config_str = config_str[1:-1]
        config_str = config_str.replace('\\"', '"').replace('\\\\', '\\')
        config = json.loads(config_str)
        logger.info(f"Loaded config: {config}")
    except Exception as e:
        logger.error(f"Failed to parse config JSON: {e}")

# Create MCP server
app = FastMCP("Airtable Tools")

# Error handling decorator
def handle_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Error in MCP handler: {str(e)}\n{error_trace}")
            return {"error": {"code": -32000, "message": str(e)}}
    wrapper.__name__ = func.__name__
    return wrapper

# Patch app.tool to use error handling
original_tool = app.tool
def patched_tool(*args, **kwargs):
    def decorator(func):
        wrapped_func = handle_exceptions(func)
        return original_tool(*args, **kwargs)(wrapped_func)
    return decorator
app.tool = patched_tool

# Get Airtable credentials from args, config or env
token = args.api_token or config.get("airtable_token") or os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN", "")
base_id = args.base_id or config.get("base_id") or os.environ.get("AIRTABLE_BASE_ID", "")

if not token:
    logger.warning("No Airtable API token provided. Use --token, --config, or set AIRTABLE_PERSONAL_ACCESS_TOKEN")
else:
    logger.info("Airtable authentication configured")

if base_id:
    logger.info(f"Using base ID: {base_id}")
else:
    logger.warning("No base ID provided. Use --base, --config, or set AIRTABLE_BASE_ID")

# Helper function for Airtable API
async def api_call(endpoint, method="GET", data=None, params=None):
    if not token:
        return {"error": "No Airtable API token provided."}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except requests_exceptions.Timeout:
        return {"error": f"Request to Airtable timed out after {REQUEST_TIMEOUT_SECONDS}s"}
    except Exception as e:
        return {"error": str(e)}

# MCP tools
@app.tool()
async def list_bases() -> str:
    result = await api_call("meta/bases")
    if "error" in result:
        return f"Error: {result['error']}"
    bases = result.get("bases", [])
    return "\n".join([f"{i+1}. {b['name']} (ID: {b['id']})" for i, b in enumerate(bases)]) or "No bases found."

@app.tool()
async def list_tables(base_id_param: Optional[str] = None) -> str:
    current_base = base_id_param or base_id
    if not current_base:
        return "No base ID provided."
    result = await api_call(f"meta/bases/{current_base}/tables")
    if "error" in result:
        return f"Error: {result['error']}"
    tables = result.get("tables", [])
    return "\n".join([f"{i+1}. {t['name']} (ID: {t['id']})" for i, t in enumerate(tables)]) or "No tables found."

@app.tool()
async def list_records(table_name: str, max_records: Optional[int] = 100, filter_formula: Optional[str] = None) -> str:
    if not base_id:
        return "No base ID set."
    params = {"maxRecords": max_records}
    if filter_formula:
        params["filterByFormula"] = filter_formula
    result = await api_call(f"{base_id}/{table_name}", params=params)
    if "error" in result:
        return f"Error: {result['error']}"
    records = result.get("records", [])
    return "\n".join([f"{i+1}. {r['id']} - {r.get('fields', {})}" for i, r in enumerate(records)]) or "No records found."

@app.tool()
async def set_base_id(base_id_param: str) -> str:
    global base_id
    base_id = base_id_param
    return f"Base ID set to: {base_id}"

# Start server
if __name__ == "__main__":
    host = os.environ.get("HOST", args.host)
    port = int(os.environ.get("PORT", args.port))
    logger.info(f"Starting server on {host}:{port}")
    app.run()
