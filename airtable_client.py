
"""
Airtable client for MCP Server with secure token management
Complete integration with all Airtable API scopes:
- data.records:read/write
- data.recordComments:read/write
- schema.bases:read/write
- webhook:manage
- block:manage
- user.email:read
"""
import aiohttp
from datetime import datetime, timedelta
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

    # ========================================
    # RECORD COMMENTS (data.recordComments)
    # ========================================

    async def get_record_comments(self, base_id: str, table_id: str, record_id: str) -> Dict:
        """Get comments for a record"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}/comments",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting record comments: {error}")
                return await response.json()

    async def create_record_comment(self, base_id: str, table_id: str, record_id: str, text: str) -> Dict:
        """Create a comment on a record"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"text": text}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}/comments",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error creating record comment: {error}")
                return await response.json()

    async def update_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str, text: str) -> Dict:
        """Update a comment on a record"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"text": text}
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error updating record comment: {error}")
                return await response.json()

    async def delete_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str) -> Dict:
        """Delete a comment from a record"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error deleting record comment: {error}")
                return await response.json()

    # ========================================
    # USER INFO (user.email:read)
    # ========================================

    async def get_user_info(self) -> Dict:
        """Get current user information including email"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airtable.com/v0/meta/whoami",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting user info: {error}")
                return await response.json()

    # ========================================
    # SCHEMA MANAGEMENT (schema.bases:write)
    # ========================================

    async def create_field(self, base_id: str, table_id: str, field_config: Dict[str, Any]) -> Dict:
        """Create a new field in a table"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"fields": [field_config]}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error creating field: {error}")
                return await response.json()

    async def update_field(self, base_id: str, table_id: str, field_id: str, field_config: Dict[str, Any]) -> Dict:
        """Update a field in a table"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
                headers=headers,
                json=field_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error updating field: {error}")
                return await response.json()

    async def delete_field(self, base_id: str, table_id: str, field_id: str) -> Dict:
        """Delete a field from a table"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error deleting field: {error}")
                return await response.json()

    async def create_table(self, base_id: str, table_config: Dict[str, Any]) -> Dict:
        """Create a new table in a base"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
                headers=headers,
                json=table_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error creating table: {error}")
                return await response.json()

    async def update_table(self, base_id: str, table_id: str, table_config: Dict[str, Any]) -> Dict:
        """Update a table in a base"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}",
                headers=headers,
                json=table_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error updating table: {error}")
                return await response.json()

    async def delete_table(self, base_id: str, table_id: str) -> Dict:
        """Delete a table from a base"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error deleting table: {error}")
                return await response.json()

    # ========================================
    # WEBHOOKS (webhook:manage)
    # ========================================

    async def list_webhooks(self, base_id: str) -> Dict:
        """List all webhooks for a base"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/webhooks",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error listing webhooks: {error}")
                return await response.json()

    async def create_webhook(self, base_id: str, webhook_config: Dict[str, Any]) -> Dict:
        """Create a new webhook for a base"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/webhooks",
                headers=headers,
                json=webhook_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error creating webhook: {error}")
                return await response.json()

    async def delete_webhook(self, base_id: str, webhook_id: str) -> Dict:
        """Delete a webhook from a base"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/webhooks/{webhook_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error deleting webhook: {error}")
                return await response.json()

    async def get_webhook_payloads(self, base_id: str, webhook_id: str) -> Dict:
        """Get webhook payloads for debugging"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/webhooks/{webhook_id}/payloads",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting webhook payloads: {error}")
                return await response.json()

    async def refresh_webhook(self, base_id: str, webhook_id: str) -> Dict:
        """Refresh webhook expiration"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/webhooks/{webhook_id}/refresh",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error refreshing webhook: {error}")
                return await response.json()

    # ========================================
    # BLOCKS (block:manage)
    # ========================================

    async def list_blocks(self) -> Dict:
        """List all blocks for the user"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airtable.com/v0/blocks",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error listing blocks: {error}")
                return await response.json()

    async def get_block_info(self, block_id: str) -> Dict:
        """Get detailed information about a block"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error getting block info: {error}")
                return await response.json()

    async def create_block(self, block_config: Dict[str, Any]) -> Dict:
        """Create a new block"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.airtable.com/v0/blocks",
                headers=headers,
                json=block_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error creating block: {error}")
                return await response.json()

    async def update_block(self, block_id: str, block_config: Dict[str, Any]) -> Dict:
        """Update an existing block"""
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers,
                json=block_config
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error updating block: {error}")
                return await response.json()

    async def delete_block(self, block_id: str) -> Dict:
        """Delete a block"""
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Error deleting block: {error}")
                return await response.json()
