"""
Airtable Service for API interactions
"""
import aiohttp
import os
from typing import Dict, Any, List

class AirtableService:
    def __init__(self):
        self.base_url = "https://api.airtable.com/v0"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for access tokens"""
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": os.getenv("AIRTABLE_CLIENT_ID"),
                "client_secret": os.getenv("AIRTABLE_CLIENT_SECRET"),
                "redirect_uri": os.getenv("AIRTABLE_REDIRECT_URI")
            }
            async with session.post("https://airtable.com/oauth2/v1/token", data=data) as resp:
                return await resp.json()

    async def list_bases(self, access_token: str) -> List[Dict[str, Any]]:
        """List user's Airtable bases"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/meta/bases", headers=headers) as resp:
                data = await resp.json()
                return data.get("bases", [])

    async def get_base_schema(self, base_id: str, access_token: str) -> Dict[str, Any]:
        """Get base schema including tables and fields"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/meta/bases/{base_id}/tables", headers=headers) as resp:
                return await resp.json()

    async def create_records(self, base_id: str, table_name: str, records: List[Dict], access_token: str) -> Dict[str, Any]:
        """Create records in Airtable"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"records": records}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/{base_id}/{table_name}", headers=headers, json=data) as resp:
                return await resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("AIRTABLE_CLIENT_ID"),
            "client_secret": os.getenv("AIRTABLE_CLIENT_SECRET")
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://airtable.com/oauth2/v1/token", data=data) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    raise Exception(f"Token refresh failed: {error_text}")
