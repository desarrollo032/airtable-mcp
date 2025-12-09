"""
OAuth Handler for Airtable MCP Server
Handles OAuth 2.0 flow for Airtable authentication
"""
import os
import json
import secrets
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from aiohttp import web
import jwt
from dotenv import load_dotenv

load_dotenv()

class AirtableOAuthHandler:
    def __init__(self):
        self.client_id = os.getenv("AIRTABLE_CLIENT_ID")
        self.client_secret = os.getenv("AIRTABLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/oauth/callback")
        self.airtable_auth_url = "https://airtable.com/oauth2/v1/authorize"
        self.airtable_token_url = "https://airtable.com/oauth2/v1/token"
        self.airtable_scopes = os.getenv("AIRTABLE_SCOPES", "data.records:read data.records:write schema.bases:read")

        # In-memory storage for demo - replace with proper storage in production
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.states: Dict[str, Dict[str, Any]] = {}

    async def start_oauth_flow(self, platform: str = "chatgpt") -> str:
        """Start OAuth flow and return state"""
        state = secrets.token_urlsafe(32)
        self.states[state] = {
            "platform": platform,
            "created_at": datetime.utcnow().isoformat()
        }

        auth_url = (
            f"{self.airtable_auth_url}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={self.airtable_scopes}&"
            f"state={state}"
        )

        return auth_url

    async def complete_oauth_flow(self, code: str, state: str) -> Dict[str, Any]:
        """Complete OAuth flow and store tokens"""
        if state not in self.states:
            raise ValueError("Invalid state parameter")

        state_data = self.states.pop(state)

        # Exchange code for tokens
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            async with session.post(self.airtable_token_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"OAuth token exchange failed: {error_text}")

                token_data = await response.json()

        # Store tokens (in production, use proper database)
        user_id = secrets.token_urlsafe(16)  # Generate user ID
        self.tokens[user_id] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            "platform": state_data["platform"]
        }

        return {
            "user_id": user_id,
            "platform": state_data["platform"],
            "expires_in": token_data.get("expires_in", 3600)
        }

    def get_user_token(self, user_id: str) -> Optional[str]:
        """Get access token for user"""
        if user_id not in self.tokens:
            return None

        token_data = self.tokens[user_id]
        if datetime.utcnow() > token_data["expires_at"]:
            # Token expired - in production, refresh token here
            return None

        return token_data["access_token"]

    async def refresh_token(self, user_id: str) -> bool:
        """Refresh expired token"""
        if user_id not in self.tokens or "refresh_token" not in self.tokens[user_id]:
            return False

        refresh_token = self.tokens[user_id]["refresh_token"]

        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            async with session.post(self.airtable_token_url, data=data) as response:
                if response.status != 200:
                    return False

                token_data = await response.json()

        # Update stored tokens
        self.tokens[user_id].update({
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", refresh_token),
            "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        })

        return True

# Global OAuth handler instance
oauth_handler = AirtableOAuthHandler()
