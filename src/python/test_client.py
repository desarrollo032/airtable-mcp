#!/usr/bin/env python3
"""
Async test client for Airtable MCP
"""
import asyncio
import os
import sys
from typing import Dict, Any
import httpx
from urllib.parse import quote_plus

# Load credentials from environment variables
TOKEN = os.environ.get('AIRTABLE_TOKEN')
BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

if not TOKEN or not BASE_ID:
    print("Error: Please set AIRTABLE_TOKEN and AIRTABLE_BASE_ID environment variables")
    print("Example: export AIRTABLE_TOKEN=your_token_here")
    print("         export AIRTABLE_BASE_ID=your_base_id_here")
    sys.exit(1)

# Basic validation
if not all(c.isalnum() or c in '-_' for c in BASE_ID):
    print(f"Error: Invalid BASE_ID format: {BASE_ID}")
    sys.exit(1)
if len(TOKEN) < 10:
    print("Error: AIRTABLE_TOKEN too short")
    sys.exit(1)

# -------------------------------
# Async Airtable API call helper
# -------------------------------
async def api_call(endpoint: str) -> Dict[str, Any]:
    if not isinstance(endpoint, str):
        raise ValueError("Endpoint must be a string")
    if '//' in endpoint or '..' in endpoint:
        raise ValueError(f"Invalid endpoint format: {endpoint}")

    url = f"https://api.airtable.com/v0/{endpoint.strip('/')}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}

# -------------------------------
# Main test routines
# -------------------------------
async def main():
    print("Testing direct Airtable API access...")

    # List bases
    print("\nListing bases:")
    result = await api_call("meta/bases")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        bases = result.get("bases", [])
        for i, base in enumerate(bases, start=1):
            print(f"{i}. {base['name']} (ID: {base['id']})")

    # List tables in the specified base
    print(f"\nListing tables in base {BASE_ID}:")
    endpoint = f"meta/bases/{quote_plus(BASE_ID)}/tables"
    result = await api_call(endpoint)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        tables = result.get("tables", [])
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table['name']} (ID: {table['id']})")
            if 'fields' in table:
                print("   Fields:")
                for field in table['fields']:
                    print(f"    - {field['name']} ({field['type']})")

# -------------------------------
# Entrypoint
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())
