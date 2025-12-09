"""
Base storage interface for MCP server
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional


class BaseStorage(ABC):
    @abstractmethod
    async def store_oauth_state(self, state: str, data: dict, ttl: int = 900):
        """Almacena estado OAuth temporalmente"""
        pass

    @abstractmethod
    async def get_oauth_state(self, state: str) -> Optional[dict]:
        """Obtiene y elimina estado OAuth"""
        pass

    @abstractmethod
    async def store_tokens(self, user_id: str, tokens: dict):
        """Almacena tokens cifrados"""
        pass

    @abstractmethod
    async def get_tokens(self, user_id: str) -> Optional[dict]:
        """Obtiene tokens descifrados"""
        pass

    @abstractmethod
    async def store_session(self, session_id: str, user_id: str, platform: str):
        """Almacena sesión MCP"""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Obtiene datos de sesión"""
        pass
