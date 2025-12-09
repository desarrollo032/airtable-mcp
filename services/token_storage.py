"""
Token Storage Service - Redis/PostgreSQL Support with Encryption
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
import asyncpg
from cryptography.fernet import Fernet

class TokenStorage:
    def __init__(self):
        self.use_redis = bool(os.getenv("REDIS_HOST"))
        self.use_postgres = bool(os.getenv("DATABASE_URL"))

        # Initialize encryption
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

        if self.use_redis:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=False  # Work with bytes for encrypted data
            )
        if self.use_postgres:
            self.postgres_pool = None

    async def init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        if self.use_postgres and not self.postgres_pool:
            self.postgres_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))

    def _encrypt(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode())

    def _decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data).decode()

    async def store_oauth_state(self, state: str, data: dict, ttl: int = 900):
        """Store OAuth state temporarily (15 minutes by default)"""
        encrypted_data = self._encrypt(json.dumps(data))
        if self.use_redis:
            self.redis.setex(f"oauth_state:{state}", ttl, encrypted_data)
        elif self.use_postgres:
            await self.init_postgres()
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO oauth_states (state, data, expires_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (state) DO UPDATE SET
                        data = EXCLUDED.data,
                        expires_at = EXCLUDED.expires_at
                """, state, encrypted_data, expires_at)

    async def get_oauth_state(self, state: str) -> Optional[dict]:
        """Get and delete OAuth state"""
        if self.use_redis:
            data = self.redis.getdel(f"oauth_state:{state}")
            if data:
                return json.loads(self._decrypt(data))
        elif self.use_postgres:
            await self.init_postgres()
            async with self.postgres_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    DELETE FROM oauth_states
                    WHERE state = $1 AND expires_at > NOW()
                    RETURNING data
                """, state)
                if row:
                    return json.loads(self._decrypt(row["data"]))
        return None

    async def store_tokens(self, session_id: str, tokens: dict):
        """Store Airtable tokens encrypted"""
        encrypted_tokens = {
            "access_token": self._encrypt(tokens["access_token"]),
            "refresh_token": self._encrypt(tokens.get("refresh_token", "")),
            "expires_at": tokens["expires_at"].isoformat(),
            "platform": tokens.get("platform", "unknown"),
            "conversation_id": tokens.get("conversation_id"),
            "created_at": datetime.utcnow().isoformat()
        }

        # Expire 5 minutes before actual token expiration
        ttl = int((tokens["expires_at"] - datetime.utcnow()).total_seconds() - 300)

        if self.use_redis:
            self.redis.setex(
                f"airtable_tokens:{session_id}",
                ttl,
                json.dumps(encrypted_tokens)
            )
        elif self.use_postgres:
            await self.init_postgres()
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO airtable_tokens (session_id, tokens, expires_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (session_id) DO UPDATE SET
                        tokens = EXCLUDED.tokens,
                        expires_at = EXCLUDED.expires_at,
                        updated_at = NOW()
                """, session_id, json.dumps(encrypted_tokens), tokens["expires_at"])

    async def get_tokens(self, session_id: str) -> Optional[dict]:
        """Get decrypted tokens"""
        if self.use_redis:
            data = self.redis.get(f"airtable_tokens:{session_id}")
            if not data:
                return None
            encrypted_tokens = json.loads(data)
        elif self.use_postgres:
            await self.init_postgres()
            async with self.postgres_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT tokens FROM airtable_tokens
                    WHERE session_id = $1 AND expires_at > NOW()
                """, session_id)
                if not row:
                    return None
                encrypted_tokens = json.loads(row["tokens"])
        else:
            return None

        return {
            "access_token": self._decrypt(encrypted_tokens["access_token"]),
            "refresh_token": self._decrypt(encrypted_tokens["refresh_token"]) if encrypted_tokens.get("refresh_token") else None,
            "expires_at": datetime.fromisoformat(encrypted_tokens["expires_at"]),
            "platform": encrypted_tokens["platform"],
            "conversation_id": encrypted_tokens["conversation_id"],
            "created_at": datetime.fromisoformat(encrypted_tokens.get("created_at", datetime.utcnow().isoformat()))
        }

    async def refresh_access_token(self, session_id: str, new_tokens: dict):
        """Update tokens when refreshed"""
        await self.store_tokens(session_id, new_tokens)

    async def delete_tokens(self, session_id: str):
        """Delete tokens for session"""
        if self.use_redis:
            self.redis.delete(f"airtable_tokens:{session_id}")
        elif self.use_postgres:
            await self.init_postgres()
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("DELETE FROM airtable_tokens WHERE session_id = $1", session_id)

    async def cleanup_expired_states(self):
        """Clean up expired OAuth states (for PostgreSQL)"""
        if self.use_postgres:
            await self.init_postgres()
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("DELETE FROM oauth_states WHERE expires_at <= NOW()")
