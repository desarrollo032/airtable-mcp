"""
Redis storage implementation for Airtable MCP Server (production)
"""
import redis.asyncio as redis
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config import settings

class RedisStorage:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=False  # Work with bytes for encrypted data
        )
        self.cipher = Fernet(settings.SECRET_KEY.encode())

    async def _encrypt(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode())

    async def _decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data).decode()

    async def store_oauth_state(self, state: str, data: dict, ttl: int = 900):
        """Store OAuth state temporarily (15 min)"""
        encrypted = await self._encrypt(json.dumps(data))
        await self.redis.setex(f"oauth_state:{state}", ttl, encrypted)

    async def get_oauth_state(self, state: str) -> dict:
        """Get and delete OAuth state"""
        data = await self.redis.getdel(f"oauth_state:{state}")
        if data:
            return json.loads(await self._decrypt(data))
        return None

    async def store_tokens(self, user_id: str, tokens: dict):
        """Store Airtable tokens encrypted"""
        encrypted_tokens = {
            "access_token": await self._encrypt(tokens["access_token"]),
            "refresh_token": await self._encrypt(tokens.get("refresh_token", "")),
            "expires_at": tokens["expires_at"].isoformat(),
            "scope": tokens.get("scope", settings.AIRTABLE_SCOPES)
        }
        ttl = int((tokens["expires_at"] - datetime.now()).total_seconds() - 300)  # 5 min before
        await self.redis.setex(
            f"user_tokens:{user_id}",
            ttl,
            json.dumps(encrypted_tokens)
        )

    async def get_tokens(self, user_id: str) -> dict:
        """Get decrypted tokens"""
        data = await self.redis.get(f"user_tokens:{user_id}")
        if not data:
            return None

        encrypted_tokens = json.loads(data)
        return {
            "access_token": await self._decrypt(encrypted_tokens["access_token"]),
            "refresh_token": await self._decrypt(encrypted_tokens["refresh_token"]),
            "expires_at": datetime.fromisoformat(encrypted_tokens["expires_at"]),
            "scope": encrypted_tokens["scope"]
        }

    async def delete_tokens(self, user_id: str):
        """Delete tokens for user"""
        await self.redis.delete(f"user_tokens:{user_id}")
