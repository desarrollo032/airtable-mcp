"""
Memory storage implementation for Airtable MCP Server (development)
"""
from datetime import datetime, timedelta
import json
from cryptography.fernet import Fernet
from config import settings

class MemoryStorage:
    def __init__(self):
        self.oauth_states = {}  # {state: data}
        self.user_tokens = {}   # {user_id: tokens}
        self.cipher = Fernet(settings.SECRET_KEY.encode())

    def _encrypt(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode())

    def _decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data).decode()

    async def store_oauth_state(self, state: str, data: dict, ttl: int = 900):
        """Store OAuth state temporarily"""
        self.oauth_states[state] = {
            "data": json.dumps(data),
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }

    async def get_oauth_state(self, state: str) -> dict:
        """Get and delete OAuth state"""
        if state not in self.oauth_states:
            return None

        state_data = self.oauth_states[state]
        if datetime.now() > state_data["expires_at"]:
            del self.oauth_states[state]
            return None

        del self.oauth_states[state]
        return json.loads(state_data["data"])

    async def store_tokens(self, user_id: str, tokens: dict):
        """Store Airtable tokens encrypted"""
        self.user_tokens[user_id] = {
            "access_token": self._encrypt(tokens["access_token"]),
            "refresh_token": self._encrypt(tokens.get("refresh_token", "")),
            "expires_at": tokens["expires_at"],
            "scope": tokens.get("scope", settings.AIRTABLE_SCOPES)
        }

    async def get_tokens(self, user_id: str) -> dict:
        """Get decrypted tokens"""
        if user_id not in self.user_tokens:
            return None

        token_data = self.user_tokens[user_id]
        if datetime.now() > token_data["expires_at"]:
            del self.user_tokens[user_id]
            return None

        return {
            "access_token": self._decrypt(token_data["access_token"]),
            "refresh_token": self._decrypt(token_data["refresh_token"]),
            "expires_at": token_data["expires_at"],
            "scope": token_data["scope"]
        }

    async def delete_tokens(self, user_id: str):
        """Delete tokens for user"""
        if user_id in self.user_tokens:
            del self.user_tokens[user_id]
