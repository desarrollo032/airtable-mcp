#!/usr/bin/env python3
"""
Airtable MCP Server adapted for FastMCP 2.x
- Compatible con ChatGPT prompts y gobernanza.
- Usage:
    python src/python/server.py
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("airtable-mcp-http")

# --- Dependencies ---
try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP SDK not found. Install with: pip install fastmcp")
    raise

# Server state
server_state = {
    "base_id": os.environ.get("AIRTABLE_BASE_ID", ""),
    "token": os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN") or os.environ.get("AIRTABLE_PAT", ""),
}

# Helper for Airtable API calls
async def api_call(endpoint, method="GET", data=None, params=None):
    import requests
    if not server_state["token"]:
        return {"error": "No Airtable API token provided."}

    headers = {"Authorization": f"Bearer {server_state['token']}", "Content-Type": "application/json"}
    url = f"https://api.airtable.com/v0/{endpoint}"

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- MCP Server Declaration ---
server = FastMCP("Airtable MCP Server")  # Must be named `server` for fastmcp run

# --- MCP Tools ---
@server.tool()
async def list_bases():
    result = await api_call("meta/bases")
    if "error" in result:
        return [f"Error: {result['error']}"]
    bases = result.get("bases", [])
    return [f"{b['name']} (ID: {b['id']})" for b in bases] or ["No bases found"]

@server.tool()
async def list_tables(base_id: Optional[str] = None):
    base = base_id or server_state["base_id"]
    if not base:
        return ["No base ID set"]
    result = await api_call(f"meta/bases/{base}/tables")
    if "error" in result:
        return [f"Error: {result['error']}"]
    tables = result.get("tables", [])
    return [f"{t['name']} (ID: {t['id']})" for t in tables] or ["No tables found"]

@server.tool()
async def list_records(table_name: str, max_records: int = 100):
    base = server_state["base_id"]
    if not base:
        return ["No base ID set"]
    params = {"maxRecords": max_records}
    result = await api_call(f"{base}/{table_name}", params=params)
    if "error" in result:
        return [f"Error: {result['error']}"]
    records = result.get("records", [])
    return [f"{r['id']}: {r.get('fields', {})}" for r in records] or ["No records found"]

@server.tool()
async def get_record(table_name: str, record_id: str):
    base = server_state["base_id"]
    if not base:
        return f"No base ID set"
    result = await api_call(f"{base}/{table_name}/{record_id}")
    if "error" in result:
        return f"Error: {result['error']}"
    return result.get("fields", {})

@server.tool()
async def create_records(table_name: str, records_json: Any):
    base = server_state["base_id"]
    if not base:
        return "No base ID set"
    try:
        records_data = json.loads(records_json) if isinstance(records_json, str) else records_json
        if not isinstance(records_data, list):
            records_data = [records_data]
        data = {"records": [{"fields": r} for r in records_data]}
        result = await api_call(f"{base}/{table_name}", method="POST", data=data)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Created {len(result.get('records', []))} records"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def update_records(table_name: str, records_json: Any):
    base = server_state["base_id"]
    if not base:
        return "No base ID set"
    try:
        records_data = json.loads(records_json) if isinstance(records_json, str) else records_json
        records = []
        for rec in records_data:
            rec_id = rec.pop("id", None)
            if not rec_id:
                return "Each record must have an 'id'"
            fields = rec.get("fields", rec)
            records.append({"id": rec_id, "fields": fields})
        data = {"records": records}
        result = await api_call(f"{base}/{table_name}", method="PATCH", data=data)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Updated {len(result.get('records', []))} records"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def delete_records(table_name: str, record_ids: Any):
    base = server_state["base_id"]
    if not base:
        return "No base ID set"
    try:
        if isinstance(record_ids, str):
            if record_ids.strip().startswith("["):
                ids = json.loads(record_ids)
            else:
                ids = [rid.strip() for rid in record_ids.split(",")]
        else:
            ids = list(record_ids)
        deleted_count = 0
        for i in range(0, len(ids), 10):
            batch = ids[i:i+10]
            params = {"records[]": batch}
            result = await api_call(f"{base}/{table_name}", method="DELETE", params=params)
            if "error" in result:
                return f"Error: {result['error']}"
            deleted_count += len(result.get("records", []))
        return f"Deleted {deleted_count} records"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def set_base_id(base_id: str):
    server_state["base_id"] = base_id
    return f"Base ID set to {base_id}"

# --- Entrypoint ---
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting Airtable MCP Server on {host}:{port}")
    server.run(transport="http", host=host, port=port)
