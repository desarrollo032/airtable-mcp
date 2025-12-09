"""
OAuth 2.0 handler for Airtable MCP Server
"""
from fastapi import HTTPException
from datetime import datetime, timedelta
import secrets
import aiohttp
from typing import Dict, Optional
from config import settings

# Seleccionar almacenamiento según entorno
if settings.ENVIRONMENT == "production":
    from storage.redis_storage import RedisStorage
    storage = RedisStorage()
else:
    from storage.memory_storage import MemoryStorage
    storage = MemoryStorage()

class AirtableOAuthHandler:
    @staticmethod
    def generate_auth_url(state: str) -> str:
        """Genera URL de autorización según documentación de Airtable"""
        params = {
            "client_id": settings.AIRTABLE_CLIENT_ID,
            "redirect_uri": settings.AIRTABLE_REDIRECT_URI,
            "response_type": "code",
            "scope": settings.AIRTABLE_SCOPES,
            "state": state
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://airtable.com/oauth2/v1/authorize?{query}"

    @staticmethod
    async def exchange_code_for_tokens(code: str) -> Dict:
        """Intercambia código por tokens según documentación de Airtable"""
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.AIRTABLE_REDIRECT_URI,
                "client_id": settings.AIRTABLE_CLIENT_ID,
                "client_secret": settings.AIRTABLE_CLIENT_SECRET
            }

            async with session.post(
                "https://airtable.com/oauth2/v1/token",
                data=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Error de Airtable OAuth: {error}"
                    )
                return await response.json()

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Dict:
        """Refresca token de acceso"""
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.AIRTABLE_CLIENT_ID,
                "client_secret": settings.AIRTABLE_CLIENT_SECRET
            }

            async with session.post(
                "https://airtable.com/oauth2/v1/token",
                data=data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Error refrescando token: {error}"
                    )
                return await response.json()

    @staticmethod
    async def start_oauth_flow(platform: str = "chatgpt") -> str:
        """Inicia flujo OAuth y retorna state"""
        state = secrets.token_urlsafe(16)
        await storage.store_oauth_state(state, {
            "platform": platform,
            "created_at": datetime.now().isoformat()
        })
        return state

    @staticmethod
    async def complete_oauth_flow(code: str, state: str) -> Dict:
        """Completa flujo OAuth y retorna user_id"""
        # Validar state
        state_data = await storage.get_oauth_state(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Estado inválido o expirado")

        # Obtener tokens
        tokens = await AirtableOAuthHandler.exchange_code_for_tokens(code)
        tokens["expires_at"] = datetime.now() + timedelta(seconds=tokens["expires_in"])

        # Crear user_id único
        user_id = secrets.token_hex(16)

        # Almacenar tokens
        await storage.store_tokens(user_id, tokens)

        return {
            "user_id": user_id,
            "platform": state_data["platform"],
            "expires_at": tokens["expires_at"].isoformat()
        }
