
#!/usr/bin/env python3
"""
Airtable MCP Inspector Server - FastMCP 2.x (Corrected)
- Async HTTP client (httpx) instead of requests to avoid blocking the event loop.
- Robust imports, safe URL building, clear error handling.
- Comprehensive Airtable integration with all scopes:
  * data.records:read/write
  * data.recordComments:read/write
  * schema.bases:read/write
  * webhook:manage
  * block:manage
  * user.email:read
- Usage:
    python src/python/inspector_server.py
"""

import os
import sys
import json
import logging
from typing import Optional, Any, List, Dict
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure repo root is on sys.path so local imports work
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Setup logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("airtable-mcp-inspector")

# Async HTTP client
try:
    import httpx
except ImportError:
    logger.exception("httpx not installed. Install with: pip install httpx")
    raise

HTTP_TIMEOUT = httpx.Timeout(60.0, connect=10.0)
HTTP_LIMITS = httpx.Limits(max_connections=20, max_keepalive_connections=10)
_http_client: Optional[httpx.AsyncClient] = None

# FastMCP import
try:
    from fastmcp import FastMCP
except ImportError:
    logger.exception("fastmcp not installed. Install with: pip install fastmcp")
    raise

# Fallback for parse_data
try:
    from auth.src.toon_utils import parse_data
except Exception:
    try:
        from src.toon_utils import parse_data
    except Exception:
        logger.warning("toon_utils.parse_data not found — using identity passthrough.")
        def parse_data(x: Any) -> Any:
            try:
                return json.loads(x) if isinstance(x, str) else x
            except Exception:
                return x

# Import AirtableService
try:
    from services.airtable_service import AirtableService
except ImportError:
    logger.exception("AirtableService not found. Make sure services/airtable_service.py exists")
    raise

# Import all new tools
try:
    from src.python.tools.comments import register_comment_tools
    from src.python.tools.schema import register_schema_tools
    from src.python.tools.webhooks_advanced import register_webhook_tools_advanced
    from src.python.tools.user_info import register_user_info_tools
    from src.python.tools.blocks import register_blocks_tools
except ImportError as e:
    logger.warning(f"Could not import some advanced tools: {e}")

# Load optional config.json
config_file = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
if os.path.exists(config_file):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in cfg.items():
            if os.environ.get(k) is None:
                os.environ[k] = str(v)
    except Exception as e:
        logger.warning("Could not load config.json: %s", e)

# Env vars
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
PORT = int(os.getenv("PORT", "8000"))

if not AIRTABLE_PERSONAL_ACCESS_TOKEN:
    logger.warning("No Airtable token found in environment variables")
if not AIRTABLE_BASE_ID:
    logger.warning("No Airtable base ID set; some tools will require set_base_id")

# Initialize MCP
mcp = FastMCP("Airtable Tools - Complete Integration")

# Initialize AirtableService
airtable_service = AirtableService()

# Encapsulated server state
class ServerState:
    def __init__(self, base_id: str = "", token: str = ""):
        self.base_id = base_id
        self.token = token

server_state = ServerState(base_id=AIRTABLE_BASE_ID, token=AIRTABLE_PERSONAL_ACCESS_TOKEN or "")

# Helper: build Airtable URL
def _airtable_url(path: str) -> str:
    path = path.lstrip("/")
    return f"https://api.airtable.com/v0/{path}"

# Async API call
def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT, limits=HTTP_LIMITS)
    return _http_client


async def api_call(endpoint: str, method: str = "GET", data: Optional[Any] = None,
                   params: Optional[dict] = None, timeout: int = 60) -> Dict[str, Any]:
    if not server_state.token:
        return {"error": "No Airtable API token provided."}

    headers = {
        "Authorization": f"Bearer {server_state.token}",
        "Content-Type": "application/json",
    }

    url = _airtable_url(endpoint)
    logger.debug("API call: %s %s", method.upper(), url)

    try:
        response = await _get_http_client().request(
            method.upper(), url, headers=headers, json=data, params=params,
            timeout=timeout,
        )
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
        except Exception:
            body = {"status_code": e.response.status_code, "text": e.response.text}
        return {"error": f"API status error: {body}"}
    except httpx.RequestError as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def _chunks(items: List[Dict[str, Any]], size: int = 10) -> List[List[Dict[str, Any]]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


# ---------------------------
# MCP Tools
# ---------------------------

@mcp.tool()
async def list_bases() -> str:
    result = await api_call("meta/bases")
    if "error" in result:
        return f"Error: {result['error']}"
    bases = result.get("bases", [])
    if not bases:
        return "No bases found."
    return "\n".join(f"{i+1}. {b.get('name','<unknown>')} (ID: {b.get('id','<no-id>')})" for i, b in enumerate(bases))

@mcp.tool()
async def list_tables(base_id_param: Optional[str] = None) -> str:
    base_id = (base_id_param or server_state.base_id or "").strip()
    if not base_id:
        return "No base ID provided. Use set_base_id or pass base_id_param."
    result = await api_call(f"meta/bases/{quote(base_id, safe='')}/tables")
    if "error" in result:
        return f"Error: {result['error']}"
    tables = result.get("tables", [])
    if not tables:
        return "No tables found."
    return "\n".join(f"{i+1}. {t.get('name','<unknown>')} (ID: {t.get('id','<no-id>')})" for i, t in enumerate(tables))

@mcp.tool()
async def list_records(table_name: str, max_records: Optional[int] = 100, filter_formula: Optional[str] = None) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    endpoint = f"{quote(server_state.base_id, safe='')}/{quote(table_name, safe='')}"
    params: Dict[str, Any] = {"maxRecords": max(1, min(int(max_records or 100), 100))}
    if filter_formula:
        params["filterByFormula"] = filter_formula
    result = await api_call(endpoint, params=params)
    if "error" in result:
        return f"Error: {result['error']}"
    records = result.get("records", [])
    if not records:
        return "No records found."
    return "\n".join(f"{i+1}. {r.get('id','<no-id>')} - {r.get('fields',{})}" for i, r in enumerate(records))

@mcp.tool()
async def create_records(table_name: str, records_json: str) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    try:
        payload = json.loads(records_json) if isinstance(records_json, str) else records_json
    except (TypeError, json.JSONDecodeError):
        return "Error: Invalid JSON for records_json."
    if isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
    elif isinstance(payload, dict):
        records = [{"fields": payload}]
    elif isinstance(payload, list):
        records = [{"fields": record} if "fields" not in record else record for record in payload]
    else:
        return "Error: records_json must contain an object or a list."
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        return "Error: records_json must contain a list of record objects."

    endpoint = f"{quote(server_state.base_id, safe='')}/{quote(table_name, safe='')}"
    created = 0
    for batch in _chunks(records):
        result = await api_call(endpoint, method="POST", data={"records": batch})
        if "error" in result:
            return f"Error: {result['error']}"
        created += len(result.get("records", []))
    return f"Successfully created {created} records."

@mcp.tool()
async def update_records(table_name: str, records_data: str) -> str:
    if not server_state.base_id:
        return "No base ID set. Use set_base_id to configure the base."
    if not table_name:
        return "Table name is required."
    try:
        parsed = parse_data(records_data)
    except Exception as e:
        return f"Error parsing records data: {e}"
    candidates: List[Dict[str, Any]] = []
    if isinstance(parsed, dict) and "records" in parsed:
        candidates = parsed["records"]
    elif isinstance(parsed, list):
        candidates = parsed
    elif isinstance(parsed, dict) and "id" in parsed:
        candidates = [parsed]
    else:
        return "Error: update_records requires records with 'id' field."
    if not isinstance(candidates, list) or not all(isinstance(record, dict) for record in candidates):
        return "Error: records_data must contain a list of record objects."
    to_send: List[Dict[str, Any]] = []
    for rec in candidates:
        if not isinstance(rec, dict) or "id" not in rec:
            return "Error: each record must have 'id' and 'fields'."
        rid = rec["id"]
        fields = rec.get("fields") or {k: v for k, v in rec.items() if k != "id"}
        to_send.append({"id": rid, "fields": fields})
    endpoint = f"{quote(server_state.base_id, safe='')}/{quote(table_name, safe='')}"
    updated = 0
    for batch in _chunks(to_send):
        result = await api_call(endpoint, method="PATCH", data={"records": batch})
        if "error" in result:
            return f"Error: {result['error']}"
        updated += len(result.get("records", []))
    return f"Successfully updated {updated} records."

@mcp.tool()
async def set_base_id(base_id_param: str) -> str:
    if not base_id_param:
        return "Error: base_id_param required."
    server_state.base_id = base_id_param
    return f"Base ID set to: {base_id_param}"

# ---------------------------
# Register all advanced tools with MCP server
# ---------------------------

# Set access token for advanced tools
mcp._access_token = server_state.token

# Register advanced tools
try:
    # Register comment tools
    register_comment_tools(mcp, airtable_service)
    logger.info("✅ Comment tools registered")
    
    # Register schema tools
    register_schema_tools(mcp, airtable_service)
    logger.info("✅ Schema tools registered")
    
    # Register webhook tools
    register_webhook_tools_advanced(mcp, airtable_service)
    logger.info("✅ Webhook tools registered")
    
    # Register user info tools
    register_user_info_tools(mcp, airtable_service)
    logger.info("✅ User info tools registered")
    
    # Register blocks tools
    register_blocks_tools(mcp, airtable_service)
    logger.info("✅ Blocks tools registered")
    
    logger.info("🎉 All advanced tools registered successfully!")
    
except Exception as e:
    logger.warning(f"Could not register advanced tools: {e}")


# ---------------------------
def main() -> None:
    if not server_state.token:
        logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set. Exiting.")
        raise SystemExit(1)

    logger.info("Starting Airtable MCP Inspector Server - Complete Integration")
    logger.info("PORT=%s", PORT)
    logger.info("Available tools: Basic + Comments + Schema + Webhooks + User Info + Blocks")
    mcp.run(transport="http", host="0.0.0.0", port=PORT)


# Entrypoint
# ---------------------------
if __name__ == "__main__":
    main()
