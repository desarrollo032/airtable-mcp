"""
MCP routes for Airtable MCP Server.
Provides endpoints for MCP operations with authentication.
"""
from flask import Blueprint, request, jsonify
from ..auth.src.server import (
    list_bases, list_tables, list_records, get_record,
    create_records, update_records, delete_records
)

mcp_bp = Blueprint('mcp', __name__)

@mcp_bp.route('/bases')
def get_bases():
    """List all accessible bases"""
    try:
        bases = list_bases()
        return jsonify({"bases": bases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/bases/<base_id>/tables')
def get_tables(base_id):
    """List tables in a base"""
    try:
        tables = list_tables(base_id)
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/tables/<table_name>/records')
def get_records(table_name):
    """List records from a table"""
    max_records = request.args.get('max_records', 100, type=int)
    try:
        records = list_records(table_name, max_records)
        return jsonify({"records": records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/tables/<table_name>/records/<record_id>')
def get_single_record(table_name, record_id):
    """Get a specific record"""
    try:
        record = get_record(table_name, record_id)
        return jsonify({"record": record})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/tables/<table_name>/records', methods=['POST'])
def create_new_records(table_name):
    """Create new records"""
    data = request.get_json()
    records_json = data.get('records')
    if not records_json:
        return jsonify({"error": "Records data required"}), 400

    try:
        result = create_records(table_name, records_json)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/tables/<table_name>/records', methods=['PUT'])
def update_existing_records(table_name):
    """Update existing records"""
    data = request.get_json()
    records_json = data.get('records')
    if not records_json:
        return jsonify({"error": "Records data required"}), 400

    try:
        result = update_records(table_name, records_json)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/tables/<table_name>/records', methods=['DELETE'])
def delete_existing_records(table_name):
    """Delete records"""
    data = request.get_json()
    record_ids = data.get('record_ids')
    if not record_ids:
        return jsonify({"error": "Record IDs required"}), 400

    try:
        result = delete_records(table_name, record_ids)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
