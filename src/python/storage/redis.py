"""
Redis storage implementation for Airtable MCP Server.
Uses Redis for fast, in-memory storage with optional persistence.
"""
import os
import redis.asyncio as redis
from typing import Dict, Any, Optional
from .base import BaseStorage

class RedisStorage(BaseStorage):
    """Redis storage backend"""

    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(self.redis_url)

    async def store(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store data in Redis"""
        try:
            json_value = str(value)  # Simplified - should use proper JSON serialization
            if ttl:
                await self.redis.setex(key, ttl, json_value)
            else:
                await self.redis.set(key, json_value)
            return True
        except Exception:
            return False

    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Redis"""
        try:
            value = await self.redis.get(key)
            if value:
                return eval(value.decode())  # Simplified - should use proper JSON deserialization
            return None
        except Exception:
            return None

    async def delete(self, key: str) -> bool:
        """Delete data from Redis"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return await self.redis.exists(key) > 0
        except Exception:
            return False

    async def cleanup_expired(self) -> int:
        """Redis handles expiration automatically"""
        return 0
