#!/usr/bin/env python3
"""
OAuth Handler for Airtable MCP Server
Handles OAuth 2.0 flow for Airtable authentication
"""

import os
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

class AirtableOAuthHandler:
    def __init__(self):
        # Usar variables consistentes para OAuth
        self.client_id = os.getenv("AIRTABLE_OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("AIRTABLE_OAUTH_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "AIRTABLE_OAUTH_REDIRECT_URI", "http://localhost:8000/airtable/callback"
        )
        self.auth_url = "https://airtable.com/oauth2/v1/authorize"
        self.token_url = "https://airtable.com/oauth2/v1/token"
        self.scopes = os.getenv(
            "AIRTABLE_OAUTH_SCOPES",
            "data.records:read data.records:write schema.bases:read"
        )

        # Almacenamiento en memoria (cambiar por DB en producción)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.states: Dict[str, Dict[str, Any]] = {}

    async def start_oauth_flow(self, platform: str = "chatgpt") -> str:
        """Start OAuth flow and return authorization URL"""
        state = secrets.token_urlsafe(32)
        self.states[state] = {
            "platform": platform,
            "created_at": datetime.utcnow().isoformat()
        }

        auth_url = (
            f"{self.auth_url}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={quote(self.scopes)}&"
            f"state={state}"
        )
        return auth_url

    async def complete_oauth_flow(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if state not in self.states:
            raise ValueError("Invalid state parameter")

        state_data = self.states.pop(state)

        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            async with session.post(self.token_url, data=data, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"OAuth token exchange failed: {text}")
                token_data = await resp.json()

        # Generar ID de usuario y almacenar token
        user_id = secrets.token_urlsafe(16)
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
        """Return access token if valid, otherwise None"""
        token_data = self.tokens.get(user_id)
        if not token_data:
            return None
        if datetime.utcnow() > token_data["expires_at"]:
            return None  # opcional: llamar refresh_token
        return token_data["access_token"]

    async def refresh_token(self, user_id: str) -> bool:
        """Refresh expired token using refresh token"""
        token_data = self.tokens.get(user_id)
        if not token_data or not token_data.get("refresh_token"):
            return False

        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": token_data["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            async with session.post(self.token_url, data=data, headers=headers) as resp:
                if resp.status != 200:
                    return False
                new_tokens = await resp.json()

        token_data.update({
            "access_token": new_tokens["access_token"],
            "refresh_token": new_tokens.get("refresh_token", token_data["refresh_token"]),
            "expires_at": datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600))
        })
        return True

# Instancia global para usar en el servidor
oauth_handler = AirtableOAuthHandler()
