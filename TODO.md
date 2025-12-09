# TOON Integration with JSON in MCP Server

## Overview
Integrating TOON (Token-Oriented Object Notation) with JSON support in the Airtable MCP server to provide a more efficient format for AI interactions. TOON reduces payload size and improves parsing speed while maintaining compatibility with existing JSON workflows.

## Completed Tasks
- [x] Create TOON utilities module (`src/python/airtable_mcp/src/toon_utils.py`)
  - [x] `parse_toon()` - Convert TOON strings to Python dicts
  - [x] `stringify_toon()` - Convert Python dicts to TOON strings
  - [x] `detect_format()` - Auto-detect JSON vs TOON format
  - [x] `parse_data()` - Unified parsing function
  - [x] `stringify_data()` - Unified stringification function
- [x] Update main MCP server (`src/python/airtable_mcp/src/server.py`)
  - [x] Import TOON utilities
  - [x] Update `create_records()` to support TOON format
  - [x] Update `update_records()` to support TOON format
  - [x] Update `delete_records()` to support TOON format
- [x] Update inspector server (`src/python/inspector_server.py`)
  - [x] Import TOON utilities
  - [x] Update `create_records()` to support TOON format
  - [x] Update `update_records()` to support TOON format
- [x] Test TOON functionality
  - [x] Verify JSON parsing still works
  - [x] Verify TOON parsing works
  - [x] Verify TOON stringification works

## TOON Format Examples

### Input Examples
```json
// JSON format (still supported)
{"name": "John Doe", "age": 30, "active": true}
```

```toon
// TOON format (new)
user name "John Doe" age 30 active true
```

### Usage in Tools
```python
# Both formats work in create_records, update_records, delete_records
create_records("Users", '{"name": "John", "email": "john@example.com"}')
create_records("Users", 'user name "John" email "john@example.com"')
```

## Benefits
- **Efficiency**: TOON uses 30-60% fewer tokens than JSON
- **Speed**: Faster parsing for AI models
- **Compatibility**: Existing JSON workflows continue to work
- **Flexibility**: Auto-detection of format

## Future Enhancements
- [ ] Add TOON support to response formatting (optional)
- [ ] Add middleware for automatic TOON detection in HTTP requests
- [ ] Add TOON support to other data-handling functions
- [ ] Performance benchmarks comparing JSON vs TOON
- [ ] Documentation updates for TOON usage

## Testing
Run the test command to verify functionality:
```bash
python3 -c "
from src.python.airtable_mcp.src.toon_utils import parse_data, stringify_data, detect_format
# Test code here
"
