#!/usr/bin/env python3
"""
Airtable MCP Server with HTTP/SSE Support for ChatGPT (corrected)
- Fixed imports, JWT verification, async wrappers, governance, and safer parsing.
- Usage:
    python src/python/server.py
  or from repo root:
    python -m src.python.server
"""

import os
import sys
import re
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Ensure repo root is on sys.path so imports like `airtable_mcp.server` work
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# --- Logging ---
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("airtable-mcp-http")

# --- Dependency checks ---
try:
    from fastmcp import MCPServer
except Exception:
    logger.exception("FastMCP SDK not found. Install with: pip install fastmcp")
    raise

# PyJWT for token verification
try:
    import jwt
    from jwt import InvalidTokenError
except Exception:
    logger.exception("PyJWT not installed. Install with: pip install PyJWT")
    raise

# Server state
server_state = {
    "base_id": os.environ.get("AIRTABLE_BASE_ID", ""),
    "token": os.environ.get("AIRTABLE_PERSONAL_ACCESS_TOKEN") or os.environ.get("AIRTABLE_PAT", ""),
}

# Helper function for Airtable API calls
async def api_call(endpoint, method="GET", data=None, params=None):
    """Make an Airtable API call"""
    import requests

    # Check if token is available before making API calls
    if not server_state["token"]:
        return {"error": "No Airtable API token provided. Please set AIRTABLE_PERSONAL_ACCESS_TOKEN"}

    headers = {
        "Authorization": f"Bearer {server_state['token']}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call error: {str(e)}")
        return {"error": str(e)}

# Define MCP tool functions as regular async functions
async def list_bases():
    """List all accessible Airtable bases"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to list your bases."

    result = await api_call("meta/bases")

    if "error" in result:
        return f"Error: {result['error']}"

    bases = result.get("bases", [])
    if not bases:
        return "No bases found accessible with your token."

    base_list = [f"{i+1}. {base['name']} (ID: {base['id']})" for i, base in enumerate(bases)]
    return "Available bases:\n" + "\n".join(base_list)

async def list_tables(base_id=None):
    """List all tables in the specified base or the default base"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to list tables."

    base = base_id or server_state["base_id"]

    if not base:
        return "Error: No base ID provided. Please specify a base_id or set AIRTABLE_BASE_ID in your .env file."

    result = await api_call(f"meta/bases/{base}/tables")

    if "error" in result:
        return f"Error: {result['error']}"

    tables = result.get("tables", [])
    if not tables:
        return "No tables found in this base."

    table_list = [f"{i+1}. {table['name']} (ID: {table['id']}, Fields: {len(table.get('fields', []))})"
                 for i, table in enumerate(tables)]
    return "Tables in this base:\n" + "\n".join(table_list)

async def list_records(table_name, max_records=100):
    """List records from a table"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to list records."

    base = server_state["base_id"]

    if not base:
        return "Error: No base ID set. Please set a base ID."

    params = {"maxRecords": max_records}

    result = await api_call(f"{base}/{table_name}", params=params)

    if "error" in result:
        return f"Error: {result['error']}"

    records = result.get("records", [])
    if not records:
        return "No records found in this table."

    # Format the records for display
    formatted_records = []
    for i, record in enumerate(records):
        record_id = record.get("id", "unknown")
        fields = record.get("fields", {})
        field_text = ", ".join([f"{k}: {v}" for k, v in fields.items()])
        formatted_records.append(f"{i+1}. ID: {record_id} - {field_text}")

    return "Records:\n" + "\n".join(formatted_records)

async def get_record(table_name, record_id):
    """Get a specific record from a table"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to get records."

    base = server_state["base_id"]

    if not base:
        return "Error: No base ID set. Please set a base ID."

    result = await api_call(f"{base}/{table_name}/{record_id}")

    if "error" in result:
        return f"Error: {result['error']}"

    fields = result.get("fields", {})
    if not fields:
        return f"Record {record_id} found but contains no fields."

    # Format the fields for display
    formatted_fields = []
    for key, value in fields.items():
        formatted_fields.append(f"{key}: {value}")

    return f"Record ID: {record_id}\n" + "\n".join(formatted_fields)

async def create_records(table_name, records_json):
    """Create records in a table from JSON"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to create records."

    base = server_state["base_id"]

    if not base:
        return "Error: No base ID set. Please set a base ID."

    try:
        records_data = json.loads(records_json)

        # Format the records for Airtable API
        if not isinstance(records_data, list):
            records_data = [records_data]

        records = [{"fields": record} for record in records_data]

        data = {"records": records}
        result = await api_call(f"{base}/{table_name}", method="POST", data=data)

        if "error" in result:
            return f"Error: {result['error']}"

        created_records = result.get("records", [])
        return f"Successfully created {len(created_records)} records."

    except json.JSONDecodeError:
        return "Error: Invalid JSON format in records_json parameter."
    except Exception as e:
        return f"Error creating records: {str(e)}"

async def update_records(table_name, records_data):
    """Update records in a table from JSON or TOON string"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to update records."

    base = server_state["base_id"]

    if not base:
        return "Error: No base ID set. Please set a base ID."

    try:
        # Auto-detect and parse JSON or TOON format
        try:
            from auth.src.toon_utils import parse_data
            parsed_data = parse_data(records_data)
        except ImportError:
            parsed_data = json.loads(records_data)

        # Handle different TOON structures
        if isinstance(parsed_data, dict):
            # If it's a dict with multiple objects, extract the records
            if 'records' in parsed_data:
                records_data = parsed_data['records']
                if not isinstance(records_data, list):
                    records_data = [records_data]
            else:
                # Single record or list of records
                records_data = list(parsed_data.values())
                if not isinstance(records_data, list):
                    records_data = [records_data]
        elif isinstance(parsed_data, list):
            records_data = parsed_data
        else:
            records_data = [parsed_data]

        # Format the records for Airtable API
        records = []
        for record in records_data:
            if "id" not in record:
                return "Error: Each record must have an 'id' field."

            rec_id = record.pop("id")
            fields = record.get("fields", record)  # Support both {id, fields} format and direct fields
            records.append({"id": rec_id, "fields": fields})

        data = {"records": records}
        result = await api_call(f"{base}/{table_name}", method="PATCH", data=data)

        if "error" in result:
            return f"Error: {result['error']}"

        updated_records = result.get("records", [])
        return f"Successfully updated {len(updated_records)} records."

    except Exception as e:
        return f"Error updating records: {str(e)}. Please provide valid JSON or TOON format."

async def delete_records(table_name, record_ids):
    """Delete records from a table by their IDs"""
    if not server_state["token"]:
        return "Please provide an Airtable API token to delete records."

    base = server_state["base_id"]

    if not base:
        return "Error: No base ID set. Please set a base ID."

    try:
        # Handle different input formats
        if isinstance(record_ids, str):
            if record_ids.startswith("["):
                ids_list = json.loads(record_ids)
            else:
                ids_list = [rid.strip() for rid in record_ids.split(",")]
        elif isinstance(record_ids, list):
            ids_list = record_ids
        else:
            ids_list = [str(record_ids)]

        # Ensure all IDs are strings
        ids_list = [str(rid) for rid in ids_list]

        # Delete records in batches of 10 (Airtable API limit)
        deleted_count = 0
        for i in range(0, len(ids_list), 10):
            batch = ids_list[i:i+10]
            params = {"records[]": batch}

            result = await api_call(f"{base}/{table_name}", method="DELETE", params=params)

            if "error" in result:
                return f"Error deleting records: {result['error']}"

            deleted_count += len(result.get("records", []))

        return f"Successfully deleted {deleted_count} records."

    except Exception as e:
        return f"Error deleting records: {str(e)}. Please provide valid format (comma-separated, JSON array, or TOON)."

async def set_base_id(base_id):
    """Set the current Airtable base ID"""
    server_state["base_id"] = base_id
    return f"Base ID set to: {base_id}"

# --- MCP Server Declaration ---
server = MCPServer(
    name="Airtable MCP Server",
    description="Airtable MCP server with ChatGPT HTTP/SSE integration (secure)",
    version=os.environ.get("MCP_SERVER_VERSION", "3.2.5"),
)

# --- Environment / Config ---
AIRTABLE_PAT = os.environ.get("AIRTABLE_PAT")  # required for Airtable SDK if used
JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME")  # should be set in production
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
# Parse allowed lists into clean lists (empty -> allow all)
def _split_env_list(key: str) -> List[str]:
    raw = os.environ.get(key, "")
    return [s.strip() for s in raw.split(",") if s.strip()]

ALLOWED_BASES = set(_split_env_list("AIRTABLE_ALLOWED_BASES"))
ALLOWED_TABLES = set(_split_env_list("AIRTABLE_ALLOWED_TABLES"))

# --- Simple in-memory rate limiter (per user or IP) ---
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "60"))  # requests per window
_rate_state: Dict[str, List[float]] = {}
_rate_lock = asyncio.Lock()

async def rate_limited(key: str) -> bool:
    """Return True if allowed, False if rate limited."""
    now = time.time()
    async with _rate_lock:
        hits = _rate_state.setdefault(key, [])
        # remove outdated
        cutoff = now - RATE_LIMIT_WINDOW
        while hits and hits[0] < cutoff:
            hits.pop(0)
        if len(hits) >= RATE_LIMIT_MAX:
            return False
        hits.append(now)
        return True

# --- Governance & Auth ---
class Governance:
    def validate_access(self, base: Optional[str], table: Optional[str], user: str) -> bool:
        """Validate access based on governance rules. If ALLOWED_* empty -> permit."""
        if ALLOWED_BASES and base and base not in ALLOWED_BASES:
            return False
        if ALLOWED_TABLES and table and table not in ALLOWED_TABLES:
            return False
        return True

class JWTVerifier:
    def verify(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token using PyJWT (HS256 by default). Returns payload on success, None otherwise."""
        if not token:
            return None
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

governance = Governance()
auth = JWTVerifier()

# --- Helpers for robust prompt parsing ---
RE_GET_RECORD = re.compile(r"get\s+record\s+(?P<table>[^\s]+)\s+(?P<id>[A-Za-z0-9_-]+)", re.I)
RE_LIST_RECORDS = re.compile(r"list\s+records\s+(?P<table>[^\s]+)(?:\s+max=(?P<max>\d+))?", re.I)
RE_LIST_TABLES = re.compile(r"list\s+tables", re.I)
RE_LIST_BASES = re.compile(r"list\s+bases", re.I)

def parse_prompt(prompt: str) -> Dict[str, Any]:
    p = prompt.strip()
    if m := RE_LIST_BASES.search(p):
        return {"action": "list_bases"}
    if m := RE_LIST_TABLES.search(p):
        return {"action": "list_tables"}
    if m := RE_LIST_RECORDS.search(p):
        return {"action": "list_records", "table": m.group("table"), "max": int(m.group("max") or 100)}
    if m := RE_GET_RECORD.search(p):
        return {"action": "get_record", "table": m.group("table"), "id": m.group("id")}
    # fallback
    return {"action": "help"}

# --- HTTP endpoint for ChatGPT queries ---
@server.http_endpoint("/chatgpt_query")
async def chatgpt_query_endpoint(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expected request JSON:
    {
      "prompt": "list records tableX max=10",
      "base": "appXXXXXXXX",
      "table": "Table Name",
      "user_token": "eyJ...",
      "client_ip": "1.2.3.4"   # optional
    }
    """
    try:
        prompt = (request.get("prompt") or "").strip()
        base = request.get("base")
        table = request.get("table")
        user_token = request.get("user_token")
        client_ip = request.get("client_ip") or request.get("client", {}).get("ip") or "anonymous"

        # Authenticate user (if token provided) — require token by default in production
        user_info = None
        if user_token:
            user_info = auth.verify(user_token)
            if not user_info:
                return {"error": "Invalid authentication token", "status": "error"}, 401

        # Determine rate-limit key (prefer user sub/jti, else ip)
        rate_key = None
        if user_info and isinstance(user_info, dict):
            rate_key = user_info.get("sub") or user_info.get("user") or user_info.get("jti")
        rate_key = rate_key or client_ip or "anonymous"

        allowed = await rate_limited(rate_key)
        if not allowed:
            return {"error": "Rate limit exceeded", "status": "error"}, 429

        # Validate governance if base/table specified
        user_for_gov = user_info.get("user") if user_info and isinstance(user_info, dict) and "user" in user_info else "anonymous"
        if base or table:
            if not governance.validate_access(base, table, user_for_gov):
                return {"error": "Access denied by governance rules", "status": "error"}, 403

        # Parse prompt robustly
        parsed = parse_prompt(prompt)
        action = parsed["action"]

        if action == "list_bases":
            result = await list_bases()
        elif action == "list_tables":
            # prefer provided base param, else parsed table as base id (if any)
            result = await list_tables(base)
        elif action == "list_records":
            table_name = parsed.get("table") or table
            if not table_name:
                return {"error": "Table name required for listing records", "status": "error"}, 400
            max_records = parsed.get("max", 100)
            result = await list_records(table_name, max_records)
        elif action == "get_record":
            table_name = parsed.get("table") or table
            record_id = parsed.get("id")
            if not table_name or not record_id:
                return {"error": "Table name and record id required", "status": "error"}, 400
            result = await get_record(table_name, record_id)
        else:
            # Help / default response
            result = {
                "help": (
                    "Available commands (use in 'prompt'): "
                    "'list bases', 'list tables', "
                    "'list records <table> [max=N]', "
                    "'get record <table> <id>'"
                )
            }

        return {"response": result, "status": "success", "timestamp": time.time()}

    except Exception as e:
        logger.exception("ChatGPT query error")
        return {"error": str(e), "status": "error"}

# --- Health check endpoint ---
@server.http_endpoint("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": server.version,
        "endpoints": ["/chatgpt_query", "/health"],
        "timestamp": time.time(),
    }

# --- MCP tools (re-export existing tools for HTTP access) ---
@server.tool()
async def list_bases_tool() -> Any:
    return await list_bases()

@server.tool()
async def list_tables_tool(base_id: Optional[str] = None) -> Any:
    return await list_tables(base_id)

@server.tool()
async def list_records_tool(table_name: str, max_records: int = 100) -> Any:
    return await list_records(table_name, max_records)

@server.tool()
async def get_record_tool(table_name: str, record_id: str) -> Any:
    return await get_record(table_name, record_id)

@server.tool()
async def create_records_tool(table_name: str, records_json: str) -> Any:
    """
    records_json: JSON string or list of record dicts; we try to parse it.
    """
    try:
        payload = json.loads(records_json) if isinstance(records_json, str) else records_json
    except Exception:
        raise ValueError("records_json must be valid JSON")
    return await create_records(table_name, payload)

@server.tool()
async def update_records_tool(table_name: str, records_json: str) -> Any:
    try:
        payload = json.loads(records_json) if isinstance(records_json, str) else records_json
    except Exception:
        raise ValueError("records_json must be valid JSON")
    return await update_records(table_name, payload)

@server.tool()
async def delete_records_tool(table_name: str, record_ids: str) -> Any:
    """
    record_ids: JSON list string or comma-separated ids
    """
    try:
        if isinstance(record_ids, str):
            if record_ids.strip().startswith("["):
                ids = json.loads(record_ids)
            else:
                ids = [i.strip() for i in record_ids.split(",") if i.strip()]
        else:
            ids = list(record_ids)
    except Exception:
        raise ValueError("record_ids must be a JSON list or comma-separated string")
    return await delete_records(table_name, ids)

@server.tool()
async def set_base_id_tool(base_id: str) -> Any:
    return await set_base_id(base_id)

# --- Entrypoint ---
if __name__ == "__main__":
    # Validate required envs (best-effort)
    if not AIRTABLE_PAT:
        logger.warning("AIRTABLE_PAT not set. Airtable calls may fail if required by underlying code.")

    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting Airtable MCP HTTP Server on {host}:{port}")
    logger.info("ChatGPT endpoint available at: /chatgpt_query")
    logger.info("Health check available at: /health")

    # run the server; FastMCP's server.run should manage the event loop
    server.run(host=host, port=port)
