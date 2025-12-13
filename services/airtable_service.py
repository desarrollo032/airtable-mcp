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

    # ========================================
    # RECORD COMMENTS (data.recordComments)
    # ========================================

    async def get_record_comments(self, base_id: str, table_id: str, record_id: str, access_token: str) -> Dict[str, Any]:
        """Get comments for a record"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/{base_id}/{table_id}/{record_id}/comments",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error getting record comments: {error}")
                return await resp.json()

    async def create_record_comment(self, base_id: str, table_id: str, record_id: str, text: str, access_token: str) -> Dict[str, Any]:
        """Create a comment on a record"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{base_id}/{table_id}/{record_id}/comments",
                headers=headers,
                json=data
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error creating record comment: {error}")
                return await resp.json()

    async def update_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str, text: str, access_token: str) -> Dict[str, Any]:
        """Update a comment on a record"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"text": text}
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.base_url}/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
                headers=headers,
                json=data
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error updating record comment: {error}")
                return await resp.json()

    async def delete_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str, access_token: str) -> Dict[str, Any]:
        """Delete a comment from a record"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/{base_id}/{table_id}/{record_id}/comments/{comment_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error deleting record comment: {error}")
                return await resp.json()

    # ========================================
    # USER INFO (user.email:read)
    # ========================================

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get current user information including email"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airtable.com/v0/meta/whoami",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error getting user info: {error}")
                return await resp.json()

    # ========================================
    # SCHEMA MANAGEMENT (schema.bases:write)
    # ========================================

    async def create_field(self, base_id: str, table_id: str, field_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Create a new field in a table"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"fields": [field_config]}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/meta/bases/{base_id}/tables/{table_id}/fields",
                headers=headers,
                json=data
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error creating field: {error}")
                return await resp.json()

    async def update_field(self, base_id: str, table_id: str, field_id: str, field_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Update a field in a table"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.base_url}/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
                headers=headers,
                json=field_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error updating field: {error}")
                return await resp.json()

    async def delete_field(self, base_id: str, table_id: str, field_id: str, access_token: str) -> Dict[str, Any]:
        """Delete a field from a table"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error deleting field: {error}")
                return await resp.json()

    async def create_table(self, base_id: str, table_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Create a new table in a base"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/meta/bases/{base_id}/tables",
                headers=headers,
                json=table_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error creating table: {error}")
                return await resp.json()

    async def update_table(self, base_id: str, table_id: str, table_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Update a table in a base"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.base_url}/meta/bases/{base_id}/tables/{table_id}",
                headers=headers,
                json=table_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error updating table: {error}")
                return await resp.json()

    async def delete_table(self, base_id: str, table_id: str, access_token: str) -> Dict[str, Any]:
        """Delete a table from a base"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/meta/bases/{base_id}/tables/{table_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error deleting table: {error}")
                return await resp.json()

    # ========================================
    # WEBHOOKS (webhook:manage)
    # ========================================

    async def list_webhooks(self, base_id: str, access_token: str) -> Dict[str, Any]:
        """List all webhooks for a base"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/meta/bases/{base_id}/webhooks",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error listing webhooks: {error}")
                return await resp.json()

    async def create_webhook(self, base_id: str, webhook_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Create a new webhook for a base"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/meta/bases/{base_id}/webhooks",
                headers=headers,
                json=webhook_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error creating webhook: {error}")
                return await resp.json()

    async def delete_webhook(self, base_id: str, webhook_id: str, access_token: str) -> Dict[str, Any]:
        """Delete a webhook from a base"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/meta/bases/{base_id}/webhooks/{webhook_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error deleting webhook: {error}")
                return await resp.json()

    async def get_webhook_payloads(self, base_id: str, webhook_id: str, access_token: str) -> Dict[str, Any]:
        """Get webhook payloads for debugging"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/meta/bases/{base_id}/webhooks/{webhook_id}/payloads",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error getting webhook payloads: {error}")
                return await resp.json()

    async def refresh_webhook(self, base_id: str, webhook_id: str, access_token: str) -> Dict[str, Any]:
        """Refresh webhook expiration"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/meta/bases/{base_id}/webhooks/{webhook_id}/refresh",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error refreshing webhook: {error}")
                return await resp.json()

    # ========================================
    # BLOCKS (block:manage)
    # ========================================

    async def list_blocks(self, access_token: str) -> Dict[str, Any]:
        """List all blocks for the user"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airtable.com/v0/blocks",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error listing blocks: {error}")
                return await resp.json()

    async def get_block_info(self, block_id: str, access_token: str) -> Dict[str, Any]:
        """Get detailed information about a block"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error getting block info: {error}")
                return await resp.json()

    async def create_block(self, block_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Create a new block"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.airtable.com/v0/blocks",
                headers=headers,
                json=block_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error creating block: {error}")
                return await resp.json()

    async def update_block(self, block_id: str, block_config: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Update an existing block"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers,
                json=block_config
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error updating block: {error}")
                return await resp.json()

    async def delete_block(self, block_id: str, access_token: str) -> Dict[str, Any]:
        """Delete a block"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"https://api.airtable.com/v0/blocks/{block_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Error deleting block: {error}")
                return await resp.json()
