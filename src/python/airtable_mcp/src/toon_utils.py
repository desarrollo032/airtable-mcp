"""
TOON (Token-Oriented Object Notation) utilities for MCP server
TOON is a lightweight format optimized for AI, reducing payload size and parsing speed.
"""

import json
from typing import Any, Dict, List, Union


def parse_toon(toon_data: str) -> Dict[str, Any]:
    """
    Parse TOON format to Python dict.

    TOON format example:
    user id123 name "John Doe" age 30
    records id456 name "Project X" status "active"

    Becomes:
    {
        "user": {"id": "id123", "name": "John Doe", "age": 30},
        "records": {"id": "id456", "name": "Project X", "status": "active"}
    }
    """
    lines = toon_data.strip().split('\n')
    result = {}

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        obj_name = parts[0]
        obj_data = {}
        i = 1

        while i < len(parts):
            if i + 1 >= len(parts):
                break

            key = parts[i]
            value_str = parts[i + 1]

            # Handle quoted strings
            if value_str.startswith('"') and value_str.endswith('"'):
                value = value_str[1:-1]
                i += 2
            # Handle numbers
            elif value_str.replace('.', '').replace('-', '').isdigit():
                value = float(value_str) if '.' in value_str else int(value_str)
                i += 2
            # Handle booleans
            elif value_str.lower() in ('true', 'false'):
                value = value_str.lower() == 'true'
                i += 2
            # Handle null
            elif value_str.lower() == 'null':
                value = None
                i += 2
            else:
                # Unquoted string or identifier
                value = value_str
                i += 2

            obj_data[key] = value

        result[obj_name] = obj_data

    return result


def stringify_toon(data: Dict[str, Any]) -> str:
    """
    Convert Python dict to TOON format.

    Example:
    {"user": {"id": "id123", "name": "John Doe", "age": 30}}

    Becomes:
    user id "id123" name "John Doe" age 30
    """
    lines = []

    for obj_name, obj_data in data.items():
        if not isinstance(obj_data, dict):
            continue

        parts = [obj_name]
        for key, value in obj_data.items():
            parts.append(key)
            if isinstance(value, str):
                parts.append(f'"{value}"')
            elif isinstance(value, bool):
                parts.append('true' if value else 'false')
            elif value is None:
                parts.append('null')
            else:
                parts.append(str(value))

        lines.append(' '.join(parts))

    return '\n'.join(lines)


def detect_format(data: str) -> str:
    """
    Detect if data is JSON or TOON format.
    Returns 'json' or 'toon'.
    """
    data = data.strip()
    if not data:
        return 'json'

    # Check if it starts with JSON indicators
    if data.startswith(('{', '[')):
        try:
            json.loads(data)
            return 'json'
        except json.JSONDecodeError:
            pass

    # Check if it looks like TOON (space-separated key-value pairs)
    lines = data.split('\n')
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            # TOON typically has object name followed by key-value pairs
            return 'toon'

    # Default to JSON
    return 'json'


def parse_data(data: str) -> Dict[str, Any]:
    """
    Parse data as either JSON or TOON, auto-detecting the format.
    """
    format_type = detect_format(data)

    if format_type == 'toon':
        return parse_toon(data)
    else:
        return json.loads(data)


def stringify_data(data: Dict[str, Any], format_type: str = 'json') -> str:
    """
    Stringify data to specified format (json or toon).
    """
    if format_type == 'toon':
        return stringify_toon(data)
    else:
        return json.dumps(data, indent=2)
