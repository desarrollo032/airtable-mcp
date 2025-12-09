"""
Authentication Service for OAuth and Token Management
"""
from typing import Optional
import redis
import os
from datetime import datetime, timedelta

class AuthService:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )

    async def store_oauth_state(self, user_id: str, state: str):
        """Store OAuth state for validation"""
        key = f"oauth_state:{state}"
        self.redis.setex(key, 600, user_id)  # 10 minutes

    async def validate_oauth_state(self, state: str) -> Optional[str]:
        """Validate OAuth state and return user_id"""
        key = f"oauth_state:{state}"
        user_id = self.redis.get(key)
        if user_id:
            self.redis.delete(key)
        return user_id

    async def store_airtable_tokens(self, user_id: str, access_token: str,
                                   refresh_token: str = None, expires_in: int = None):
        """Store Airtable tokens for user"""
        key = f"airtable_tokens:{user_id}"
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else None
        }
        self.redis.set(key, str(data))

    async def get_airtable_tokens(self, user_id: str) -> Optional[dict]:
        """Get Airtable tokens for user"""
        key = f"airtable_tokens:{user_id}"
        data = self.redis.get(key)
        return eval(data) if data else None
