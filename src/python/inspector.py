#!/usr/bin/env python3
"""
MCP Tool Inspector - Airtable MCP
Genera un manifiesto JSON de herramientas MCP compatible con Smithery
"""

import json

# Definición de herramientas MCP
tools = [
    {
        "name": "list_bases",
        "description": "List all accessible Airtable bases",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "returns": {"type": "string"}
    },
    {
        "name": "list_tables",
        "description": "List all tables in the specified base or the default base",
        "parameters": {
            "type": "object",
            "properties": {
                "base_id_param": {
                    "type": "string",
                    "description": "Optional base ID to use instead of the default"
                }
            },
            "required": []
        },
        "returns": {"type": "string"}
    },
    {
        "name": "list_records",
        "description": "List records from a table with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "Name of the table to list records from"},
                "max_records": {"type": "integer", "description": "Maximum number of records to return (default: 100)"},
                "filter_formula": {"type": "string", "description": "Optional Airtable formula to filter records"}
            },
            "required": ["table_name"]
        },
        "returns": {"type": "string"}
    },
    {
        "name": "get_record",
        "description": "Get a specific record from a table",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
                "record_id": {"type": "string"}
            },
            "required": ["table_name", "record_id"]
        },
        "returns": {"type": "string"}
    },
    {
        "name": "create_records",
        "description": "Create records in a table from JSON string",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
                "records_json": {"type": "string"}
            },
            "required": ["table_name", "records_json"]
        },
        "returns": {"type": "string"}
    },
    {
        "name": "update_records",
        "description": "Update records in a table from JSON string (requires 'id' for each record)",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
                "records_json": {"type": "string"}
            },
            "required": ["table_name", "records_json"]
        },
        "returns": {"type": "string"}
    },
    {
        "name": "set_base_id",
        "description": "Set the current Airtable base ID",
        "parameters": {
            "type": "object",
            "properties": {
                "base_id_param": {"type": "string"}
            },
            "required": ["base_id_param"]
        },
        "returns": {"type": "string"}
    }
]

# Imprimir JSON final
print(json.dumps({"tools": tools}, indent=2))
