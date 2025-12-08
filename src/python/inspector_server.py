#!/usr/bin/env python3
"""
Airtable MCP Inspector Server - FastMCP 2.x
"""
import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.json if it exists
config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Override environment variables with JSON config
            for key, value in config.items():
                os.environ[key] = str(value)
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}")

token = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")
port = int(os.getenv("PORT", 8000))  # Railway asigna automáticamente PORT

# Inicializar servidor FastMCP 2.x
from fastmcp import FastMCP

mcp = FastMCP("Airtable Tools")   # ESTE ES EL ÚNICO SERVIDOR VÁLIDO

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
        response = requests.request(method, url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --------------------------------------
# MCP TOOLS
# --------------------------------------

@mcp.tool()
async def list_bases() -> str:
    result = await api_call("meta/bases")
    if "error" in result:
        return f"Error: {result['error']}"
    bases = result.get("bases", [])
    return "\n".join([f"{i+1}. {b['name']} (ID: {b['id']})" for i, b in enumerate(bases)]) or "No bases found."


@mcp.tool()
async def list_tables(base_id_param: Optional[str] = None) -> str:
    current_base = base_id_param or base_id
    if not current_base:
        return "No base ID provided."
    result = await api_call(f"meta/bases/{current_base}/tables")
    if "error" in result:
        return f"Error: {result['error']}"
    tables = result.get("tables", [])
    return "\n".join([f"{i+1}. {t['name']} (ID: {t['id']})" for i, t in enumerate(tables)]) or "No tables found."


@mcp.tool()
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


@mcp.tool()
async def create_records(table_name: str, records_json: str) -> str:
    if not base_id:
        return "No base ID set."
    try:
        records_data = json.loads(records_json)
        if not isinstance(records_data, list):
            records_data = [records_data]
        records = [{"fields": record} for record in records_data]
        data = {"records": records}
        result = await api_call(f"{base_id}/{table_name}", method="POST", data=data)
        if "error" in result:
            return f"Error: {result['error']}"
        created_records = result.get("records", [])
        return f"Successfully created {len(created_records)} records."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in records_json parameter."
    except Exception as e:
        return f"Error creating records: {str(e)}"


@mcp.tool()
async def update_records(table_name: str, records_json: str) -> str:
    if not base_id:
        return "No base ID set."
    try:
        records_data = json.loads(records_json)
        if not isinstance(records_data, list):
            records_data = [records_data]
        records = []
        for record in records_data:
            if "id" not in record:
                return "Error: Each record must have an 'id' field."
            rec_id = record.pop("id")
            fields = record.get("fields", record)
            records.append({"id": rec_id, "fields": fields})
        data = {"records": records}
        result = await api_call(f"{base_id}/{table_name}", method="PATCH", data=data)
        if "error" in result:
            return f"Error: {result['error']}"
        updated_records = result.get("records", [])
        return f"Successfully updated {len(updated_records)} records."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in records_json parameter."
    except Exception as e:
        return f"Error updating records: {str(e)}"


@mcp.tool()
async def set_base_id(base_id_param: str) -> str:
    global base_id
    base_id = base_id_param
    return f"Base ID set to: {base_id}"


# --------------------------------------
# RUN FASTMCP SERVER (HTTP para Railway)
# --------------------------------------
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port
    )
