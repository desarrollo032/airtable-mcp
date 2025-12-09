# Airtable MCP Integration Guide

## 📋 Overview

This document provides comprehensive guidance for integrating Airtable with MCP (Model Context Protocol) servers, combining the latest Airtable API practices with robust Python client libraries.

## 🔑 Authentication

### Personal Access Tokens (PAT) - Recommended

As of February 1, 2024, Airtable deprecated legacy API keys in favor of **Personal Access Tokens (PAT)**.

#### Creating a Personal Access Token

1. Go to [Airtable Account Settings](https://airtable.com/account)
2. Navigate to "Developer Hub" → "Personal Access Tokens"
3. Click "Create Token"
4. Select required scopes:
   - `data.records:read` - Read records
   - `data.records:write` - Create/update/delete records
   - `schema.bases:read` - Read base schemas
5. Choose specific bases or "All current and future bases"

#### Environment Variables

```bash
# Production
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXXXXXXXXXX

# Preview/Development
AIRTABLE_PERSONAL_ACCESS_TOKEN_PREVIEW=patXXXXXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID_PREVIEW=appXXXXXXXXXXXXXXXXXXXXXX

# Environment selector
ENVIRONMENT=preview  # or "production"
```

### OAuth 2.0 (For Multi-User Applications)

For applications serving multiple users, implement OAuth 2.0:

1. Register your app in [Airtable Developer Hub](https://airtable.com/developers/web/api/oauth-reference)
2. Configure redirect URIs
3. Implement OAuth flow with proper scopes

## 🐍 PyAirtable Integration

### Installation

```bash
pip install pyairtable
```

### Basic Usage

```python
import os
from pyairtable import Api

# Initialize API with PAT
api = Api(os.environ['AIRTABLE_PERSONAL_ACCESS_TOKEN'])

# Connect to a table
table = api.table('appYourBaseId', 'YourTableName')

# CRUD Operations
all_records = table.all()                          # List all records
record = table.get('recId123')                     # Get single record
new_record = table.create({'Field': 'value'})      # Create record
updated = table.update('recId123', {'Field': 'new value'})  # Update
deleted = table.delete('recId123')                 # Delete
```

### Advanced Features

```python
# Batch operations
records = [
    {'fields': {'Name': 'Record 1', 'Status': 'Active'}},
    {'fields': {'Name': 'Record 2', 'Status': 'Pending'}}
]
created = table.batch_create(records)
updated = table.batch_update([
    {'id': 'recId1', 'fields': {'Status': 'Complete'}},
    {'id': 'recId2', 'fields': {'Status': 'Cancelled'}}
])
deleted = table.batch_delete(['recId1', 'recId2'])

# Filtering and sorting
records = table.all(
    formula="AND({Status}='Active', {Priority}='High')",
    sort=['-Created', 'Name']
)

# Pagination
page1 = table.all(max_records=100)
page2 = table.all(max_records=100, offset=page1.offset)
```

## 🏗️ MCP Server Integration

### Current Implementation Status

The MCP servers currently use direct environment variable loading:

```python
# Current approach (needs modernization)
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
```

### Recommended Architecture

```python
from pyairtable import Api
from dotenv import load_dotenv
import os

load_dotenv()

class AirtableService:
    def __init__(self):
        # Environment-based token selection
        environment = os.getenv("ENVIRONMENT", "production")

        if environment == "preview":
            token = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN_PREVIEW")
            base_id = os.getenv("AIRTABLE_BASE_ID_PREVIEW")
        else:
            token = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
            base_id = os.getenv("AIRTABLE_BASE_ID")

        if not token:
            raise ValueError("Airtable token not configured")

        self.api = Api(token)
        self.base_id = base_id

    def get_table(self, table_name: str):
        """Get table instance for operations"""
        return self.api.table(self.base_id, table_name)
```

### MCP Tool Integration

```python
from fastmcp import FastMCP
from .airtable_service import AirtableService

server = FastMCP("Airtable MCP Server")
airtable = AirtableService()

@server.tool()
async def list_records(table_name: str, max_records: int = 100):
    """List records from Airtable table"""
    try:
        table = airtable.get_table(table_name)
        records = table.all(max_records=max_records)

        return {
            "records": records,
            "count": len(records)
        }
    except Exception as e:
        return {"error": str(e)}

@server.tool()
async def create_record(table_name: str, fields: dict):
    """Create a new record in Airtable"""
    try:
        table = airtable.get_table(table_name)
        record = table.create(fields)

        return {
            "success": True,
            "record": record
        }
    except Exception as e:
        return {"error": str(e)}
```

## 🔧 Configuration

### Environment-Based Configuration

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = "production"

    # Production tokens
    airtable_token: str = ""
    airtable_base_id: str = ""

    # Preview tokens
    airtable_token_preview: str = ""
    airtable_base_id_preview: str = ""

    class Config:
        env_file = ".env"

    @property
    def active_token(self) -> str:
        if self.environment == "preview":
            return self.airtable_token_preview or self.airtable_token
        return self.airtable_token

    @property
    def active_base_id(self) -> str:
        if self.environment == "preview":
            return self.airtable_base_id_preview or self.airtable_base_id
        return self.airtable_base_id

settings = Settings()
```

## 🚀 Deployment Considerations

### Environment Variables Structure

```bash
# .env
ENVIRONMENT=preview

# Production
AIRTABLE_PERSONAL_ACCESS_TOKEN=patXXXXXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXXXXXXXXXX

# Preview/Development
AIRTABLE_PERSONAL_ACCESS_TOKEN_PREVIEW=patXXXXXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID_PREVIEW=appXXXXXXXXXXXXXXXXXXXXXX
```

### MCP Client Configurations

#### Claude Desktop

```json
{
  "mcpServers": {
    "airtable": {
      "command": "python",
      "args": ["-m", "src.python.server"],
      "env": {
        "ENVIRONMENT": "preview"
      }
    }
  }
}
```

#### ChatGPT MCP

```json
{
  "mcpServers": {
    "airtable": {
      "command": "python",
      "args": ["src/python/server.py"],
      "env": {
        "AIRTABLE_PERSONAL_ACCESS_TOKEN": "your_token_here",
        "AIRTABLE_BASE_ID": "your_base_id_here"
      }
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Verify PAT is correct and has required scopes
   - Check if base is accessible with the token

2. **"Base not found"**
   - Verify base ID is correct
   - Ensure token has access to the base

3. **Rate Limiting**
   - Airtable has rate limits; implement retry logic
   - Consider caching for read-heavy operations

### Best Practices

1. **Error Handling**: Always wrap API calls in try-catch
2. **Rate Limiting**: Implement exponential backoff
3. **Caching**: Cache metadata (bases, tables) when possible
4. **Logging**: Log API calls for debugging
5. **Validation**: Validate input data before API calls

## 📚 Additional Resources

- [Airtable API Documentation](https://airtable.com/developers/web/api/introduction)
- [Personal Access Tokens Guide](https://airtable.com/developers/web/api/authentication)
- [OAuth Reference](https://airtable.com/developers/web/api/oauth-reference)
- [PyAirtable Documentation](https://pyairtable.readthedocs.io/)
- [PyAirtable GitHub](https://github.com/gtalarico/pyairtable)
