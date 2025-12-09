"""
OAuth 2.0 authentication handler for Airtable MCP Server.
Handles OAuth flows for secure authentication.
"""
import os
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode

class OAuthHandler:
    def __init__(self):
        self.client_id = os.environ.get("AIRTABLE_CLIENT_ID")
        self.client_secret = os.environ.get("AIRTABLE_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/callback")
        self.airtable_auth_url = "https://airtable.com/oauth2/v1/authorize"
        self.airtable_token_url = "https://airtable.com/oauth2/v1/token"

    def get_authorization_url(self, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "data.records:read data.records:write schema.bases:read",
        }
        if state:
            params["state"] = state
        return f"{self.airtable_auth_url}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            response = requests.post(self.airtable_token_url, data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code,
                "grant_type": "authorization_code"
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"OAuth token exchange failed: {e}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        try:
            response = requests.post(self.airtable_token_url, data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token refresh failed: {e}")
            return None
