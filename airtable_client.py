"""
Airtable client for MCP Server with secure token management
"""
import aiohttp
from datetime import datetime
from typing import Dict, List, Any
from oauth_handler import storage, AirtableOAuthHandler

class AirtableClient:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def _get_access_token(self) -> str:
        """Get valid access token (refresh if necessary)"""
        tokens = await storage.get_tokens(self.user_id)
        if not tokens:
            raise Exception("User not authenticated")

        if datetime.now() > tokens["expires_at"]:
            if tokens.get("refresh_token"):
                new_tokens = await AirtableOAuthHandler.refresh_access_token(
                    tokens["refresh_token"]
                )
                new_tokens["expires_at"] = datetime.now() + timedelta(
                    seconds=new_tokens["expires_in"]
                )
                await storage.store_tokens(self.user_id, new_tokens)
                return new_tokens["access_token"]
            else:
                raise Exception("Token expired and no refresh token available")

        return tokens["access_token"]

    async def get_bases(self) -> List[Dict]:
        """List user's Airtable bases"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airtable.com/v0/meta/bases",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting bases: {error}")
                data = await response.json()
                return data.get("bases", [])

    async def get_table_schema(self, base_id: str) -> Dict:
        """Get schema of a table"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting schema: {error}")
                return await response.json()

    async def query_records(self, base_id: str, table_id: str, **params) -> Dict:
        """Query records"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/{base_id}/{table_id}",
                headers=headers,
                params=params
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error querying records: {error}")
                return await response.json()
