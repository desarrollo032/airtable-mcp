"""
Direct authentication handler for Airtable MCP Server.
Handles direct API key authentication without OAuth.
"""
import os
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class DirectAuthHandler:
    """Direct API key authentication handler"""

    def __init__(self):
        self.api_key = os.environ.get("AIRTABLE_API_KEY")
        self.allowed_keys = os.environ.get("ALLOWED_API_KEYS", "").split(",")
        self.session_timeout = int(os.environ.get("SESSION_TIMEOUT", 3600))  # 1 hour default

    def authenticate(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Authenticate using API key"""
        if not api_key:
            return None

        # Check if API key is allowed
        if self.allowed_keys and api_key not in self.allowed_keys:
            return None

        # Verify API key format (basic check)
        if not self._validate_api_key_format(api_key):
            return None

        # Create session token
        session_token = self._generate_session_token()
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_timeout)

        return {
            "user_id": self._hash_api_key(api_key),
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "permissions": ["read", "write"]  # Default permissions
        }

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        # In a real implementation, this would check against stored sessions
        # For now, return a mock validation
        if not session_token:
            return None

        # Check if session is expired (simplified)
        return {
            "user_id": "user123",
            "permissions": ["read", "write"]
        }

    def _validate_api_key_format(self, api_key: str) -> bool:
        """Basic validation of API key format"""
        # Airtable API keys typically start with 'pat' for personal access tokens
        return api_key.startswith('pat') and len(api_key) > 10

    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for user identification"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
