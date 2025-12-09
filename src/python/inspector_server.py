#!/usr/bin/env python3
"""
Airtable MCP Inspector Server - FastMCP 2.x (Corrected)
- Async HTTP client (httpx) instead of requests to avoid blocking the event loop.
- Robust imports, safe URL building, clear error handling.
- Usage:
    python src/python/inspector_server.py
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional, Any, List, Dict
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure repo root is on sys.path so local imports work (adjust if your layout differs)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Setup logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("airtable-mcp-inspector")

# Async HTTP client
try:
    import httpx
except Exception:
    logger.exception("httpx not installed. Install with: pip install httpx")
    raise

# FastMCP import (assumes fastmcp provided the named class/functionality)
try:
    from fastmcp import FastMCP
except Exception:
    logger.exception("fastmcp not installed or import failed. Install with: pip install fastmcp")
    raise

# Try to import parse_data from project; provide fallback stub if missing
try:
    from auth.src.toon_utils import parse_data  # preferred
except Exception:
    try:
        from src.toon_utils import parse_data  # fallback
    except Exception:
        logger.warning("toon_utils.parse_data not found — using identity passthrough.")
        def parse_data(x: Any) -> Any:
            # trivial parser fallback: try JSON then return original
            try:
                return json.loads(x) if isinstance(x, str) else x
            except Exception:
                return x

# Load config.json (optional) and override env vars (safe)
config_file = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
if os.path.exists(config_file):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in cfg.items():
            # don't clobber an already set environment variable
            if os.environ.get(k) is None:
                os.environ[k] = str(v)
    except Exception as e:
        logger.warning("Could not load config.json: %s", e)

# Environment variables and defaults
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
PORT = int(os.getenv("PORT", "8000"))

# Initialize FastMCP server
mcp = FastMCP("Airtable Tools")

# Encapsulated server state
class ServerState:
    def __init__(self, base_id: str = "", token: str = ""):
        self.base_id = base_id
        self.token = token

server_state = ServerState(base_id=AIRTABLE_BASE_ID, token=AIRTABLE_PERSONAL_ACCESS_TOKEN or "")

# Helper: build airtable URL for given endpoint (endpoint relative to v0/)
def _airtable_url(path: str) -> str:
    # path examples: "meta/bases" or "<base_id>/<table_name>"
    path = path.lstrip("/")
    return f"https://api.airtable.com/v0/{path}"

# Async API call using httpx.AsyncClient
async def api_call(endpoint: str, method: str = "GET", data: Optional[Any] = None, params: Optional[dict] = None, timeout: int = 30) -> Dict[str, Any]:
    if not server_state.token:
        return {"error": "No Airtable API token provided."}

    headers = {
        "Authorization": f"Bearer {server_state.token}",
        "Content-Type": "application/json",
    }

    url = _airtable_url(endpoint)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(method.upper(), url, headers=headers, json=data, params=params)
            response.raise_for_status()
            # Some endpoints might return plain text; try json safe
            try:
                return response.json()
            except Exception:
                return {"raw": response.text}
        except httpx.HTTPStatusError as e:
            # Try to decode JSON error message if present
            try:
                body = e.response.json()
            except Exception:
                body = {"status_code": e.response.status_code, "text": e.response.text}
            return {"error": f"API status error: {body}"}
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

# --------------------------------------
# MCP TOOLS (async)
# --------------------------------------

@mcp.tool()
async def list_bases() -> str:
    result = await api_call("meta/bases")
    if "error" in result:
        return f"Error: {result['error']}"
    bases = result.get("bases", [])
    if not bases:
        return "No bases found."
    out = []
    for i, b in enumerate(bases, start=1):
        name = b.get("name", "<unknown>")
        bid = b.get("id", "<no-id>")
        out.append(f"{i}. {name} (ID: {bid})")
    return "\n".join(out)

@mcp.tool()
async def list_tables(base_id_param: Optional[str] = None) -> str:
    base_id = (base_id_param or server_state.base_id or "").strip()
    if not base_id:
        return "No base ID provided. Use set_base_id or pass base_id_param."
    result = await api_call(f"meta/bases/{quote_plus(base_id)}/tables")
    if "error" in result:
        return f"Error: {result['error']}"
    tables = result.get("tables", [])
    if not tables:
        return "No tables found."
    out = []
    for i, t in enumerate(tables, start=1):
        name = t.get("name", "<unknown>")
        tid = t.get("id", "<no-id>")
        out.append(f"{i}. {name} (ID: {tid})")
    return "\n".join(out)

@mcp.tool()
async def list_records(table_name: str, max_records: Optional[int] = 100, filter_formula: Optional[str] = None) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    # Airtable expects table name/url encoded
    endpoint = f"{quote_plus(server_state.base_id)}/{quote_plus(table_name)}"
    params: Dict[str, Any] = {"maxRecords": int(max_records or 100)}
    if filter_formula:
        params["filterByFormula"] = filter_formula
    result = await api_call(endpoint, params=params)
    if "error" in result:
        return f"Error: {result['error']}"
    records = result.get("records", [])
    if not records:
        return "No records found."
    lines: List[str] = []
    for i, r in enumerate(records, start=1):
        rid = r.get("id", "<no-id>")
        fields = r.get("fields", {})
        lines.append(f"{i}. {rid} - {fields}")
    return "\n".join(lines)

@mcp.tool()
async def create_records(table_name: str, records_json: str) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    try:
        payload = json.loads(records_json) if isinstance(records_json, str) else records_json
    except Exception:
        return "Error: Invalid JSON for records_json."
    if isinstance(payload, dict) and "records" not in payload:
        # assume single record fields object
        payload = {"records": [{"fields": payload}]}
    elif isinstance(payload, list):
        payload = {"records": [{"fields": r} if not ("fields" in r) else r for r in payload]}
    endpoint = f"{quote_plus(server_state.base_id)}/{quote_plus(table_name)}"
    result = await api_call(endpoint, method="POST", data=payload)
    if "error" in result:
        return f"Error: {result['error']}"
    created = result.get("records", [])
    return f"Successfully created {len(created)} records."

@mcp.tool()
async def update_records(table_name: str, records_data: str) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    try:
        # parse_data may accept various formats (TOON or JSON)
        parsed = parse_data(records_data)
    except Exception as e:
        return f"Error parsing records data: {e}"
    # Normalize to list of {id, fields}
    candidates = []
    if isinstance(parsed, dict) and "records" in parsed:
        candidates = parsed["records"]
    elif isinstance(parsed, list):
        candidates = parsed
    elif isinstance(parsed, dict):
        # if dict mapping ids to fields or single record
        # detect { "id": "...", "fields": {...} } or { "recId": { ... } }
        if "id" in parsed:
            candidates = [parsed]
        else:
            # treat as single fields dict -> error because id required for update
            return "Error: update_records requires records with 'id' field."
    else:
        return "Error: Unsupported records_data format."

    to_send = []
    for rec in candidates:
        if not isinstance(rec, dict) or "id" not in rec:
            return "Error: each record must be a dict containing 'id' and 'fields' (or field keys)."
        rid = rec["id"]
        fields = rec.get("fields") or {k: v for k, v in rec.items() if k != "id"}
        to_send.append({"id": rid, "fields": fields})

    endpoint = f"{quote_plus(server_state.base_id)}/{quote_plus(table_name)}"
    data = {"records": to_send}
    result = await api_call(endpoint, method="PATCH", data=data)
    if "error" in result:
        return f"Error: {result['error']}"
    updated = result.get("records", [])
    return f"Successfully updated {len(updated)} records."

@mcp.tool()
async def set_base_id(base_id_param: str) -> str:
    if not base_id_param:
        return "Error: base_id_param required."
    server_state.base_id = base_id_param
    return f"Base ID set to: {base_id_param}"

# --------------------------------------
# Entrypoint
# --------------------------------------
if __name__ == "__main__":
    if not server_state.token:
        logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set. Exiting.")
        raise SystemExit(1)

    logger.info("Starting Airtable MCP Inspector Server")
    logger.info("Make sure PORT env var (or Railway) is set. Defaulting to %s", PORT)

    # Run the MCP server using HTTP transport to be compatible with Railway/containers
    # FastMCP's run method should be non-blocking-friendly
    mcp.run(transport="http", host="0.0.0.0", port=PORT)
