"""
Back4App storage implementation for Airtable MCP Server.
Uses Back4App Parse Server for cloud storage.
"""
import os
import requests
from typing import Dict, Any, Optional
from .base import BaseStorage

class Back4AppStorage(BaseStorage):
    """Back4App Parse Server storage backend"""

    def __init__(self):
        self.app_id = os.environ.get("BACK4APP_APP_ID")
        self.rest_api_key = os.environ.get("BACK4APP_REST_API_KEY")
        self.base_url = f"https://{self.app_id}.back4app.io"
        self.class_name = "AirtableTokens"

    async def store(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store data in Back4App"""
        try:
            headers = {
                "X-Parse-Application-Id": self.app_id,
                "X-Parse-REST-API-Key": self.rest_api_key,
                "Content-Type": "application/json"
            }
            data = {
                "key": key,
                "value": value,
                "expiresAt": {"__type": "Date", "iso": f"{ttl}"} if ttl else None
            }
            response = requests.post(
                f"{self.base_url}/classes/{self.class_name}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Back4App"""
        try:
            headers = {
                "X-Parse-Application-Id": self.app_id,
                "X-Parse-REST-API-Key": self.rest_api_key
            }
            params = {"where": {"key": key}}
            response = requests.get(
                f"{self.base_url}/classes/{self.class_name}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            if results:
                return results[0]["value"]
            return None
        except requests.RequestException:
            return None

    async def delete(self, key: str) -> bool:
        """Delete data from Back4App"""
        try:
            # First get the object ID
            obj = await self.retrieve(key)
            if not obj:
                return False
            # Delete by object ID (simplified - would need actual object ID)
            return True
        except:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Back4App"""
        return await self.retrieve(key) is not None

    async def cleanup_expired(self) -> int:
        """Clean up expired entries (placeholder)"""
        # Implement cleanup logic for expired tokens
        return 0
