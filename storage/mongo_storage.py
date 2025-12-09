"""
MongoDB storage implementation for MCP server
Supports both direct MongoDB and Back4App/Parse connections
"""
from storage.base_storage import BaseStorage
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config import settings
import json


class MongoStorage(BaseStorage):
    def __init__(self):
        # Conexión a MongoDB (Back4App/Parse)
        if settings.PARSE_APP_ID and settings.PARSE_API_KEY:
            # Conexión a Parse Server (Back4App)
            try:
                from parse import Parse
                Parse.initialize(settings.PARSE_APP_ID, settings.PARSE_API_KEY)
                self.use_parse = True
            except ImportError:
                raise ImportError("Parse SDK not installed. Install with: pip install parse")
        else:
            # Conexión directa a MongoDB
            if not settings.MONGODB_URI:
                raise ValueError("MONGODB_URI not configured")
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.use_parse = False

        self.cipher = Fernet(settings.SECRET_KEY.encode())

    async def store_oauth_state(self, state: str, data: dict, ttl: int = 900):
        """Almacena estado OAuth en MongoDB"""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        data["expires_at"] = expires_at

        if self.use_parse:
            try:
                from parse import ParseObject
                OAuthState = ParseObject("OAuthState")
                oauth_state = OAuthState()
                oauth_state.state = state
                oauth_state.data = json.dumps(data)
                oauth_state.expires_at = expires_at
                await oauth_state.save()
            except Exception as e:
                raise Exception(f"Parse OAuth state storage failed: {str(e)}")
        else:
            try:
                self.db.oauth_states.update_one(
                    {"state": state},
                    {"$set": data},
                    upsert=True
                )
                # Programar eliminación automática (TTL index)
                self.db.oauth_states.create_index("expires_at", expireAfterSeconds=0)
            except PyMongoError as e:
                raise Exception(f"MongoDB OAuth state storage failed: {str(e)}")

    async def get_oauth_state(self, state: str) -> Optional[dict]:
        """Obtiene y elimina estado OAuth"""
        if self.use_parse:
            try:
                from parse import Query
                OAuthState = Query("OAuthState")
                oauth_state = await OAuthState.get_first(state=state)

                if not oauth_state:
                    return None

                if datetime.utcnow() > oauth_state.expires_at.replace(tzinfo=None):
                    await oauth_state.destroy()
                    return None

                data = json.loads(oauth_state.data)
                await oauth_state.destroy()
                return data
            except Exception as e:
                return None
        else:
            try:
                state_doc = self.db.oauth_states.find_one_and_delete({"state": state})
                if not state_doc or datetime.utcnow() > state_doc["expires_at"]:
                    return None
                return state_doc["data"]
            except PyMongoError:
                return None

    async def store_tokens(self, user_id: str, tokens: dict):
        """Almacena tokens cifrados en MongoDB"""
        encrypted_tokens = {
            "access_token": self.cipher.encrypt(tokens["access_token"].encode()).decode(),
            "refresh_token": self.cipher.encrypt(tokens.get("refresh_token", "").encode()).decode(),
            "expires_at": tokens["expires_at"],
            "scope": tokens.get("scope", settings.AIRTABLE_SCOPES)
        }

        if self.use_parse:
            try:
                from parse import ParseObject
                UserToken = ParseObject("UserToken")
                user_token = UserToken()
                user_token.user_id = user_id
                user_token.tokens = json.dumps(encrypted_tokens)
                user_token.expires_at = tokens["expires_at"]
                await user_token.save()
            except Exception as e:
                raise Exception(f"Parse token storage failed: {str(e)}")
        else:
            try:
                self.db.user_tokens.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "tokens": encrypted_tokens,
                        "expires_at": tokens["expires_at"]
                    }},
                    upsert=True
                )
                # Programar eliminación automática
                self.db.user_tokens.create_index("expires_at", expireAfterSeconds=0)
            except PyMongoError as e:
                raise Exception(f"MongoDB token storage failed: {str(e)}")

    async def get_tokens(self, user_id: str) -> Optional[dict]:
        """Obtiene tokens descifrados desde MongoDB"""
        if self.use_parse:
            try:
                from parse import Query
                UserToken = Query("UserToken")
                user_token = await UserToken.get_first(user_id=user_id)

                if not user_token:
                    return None

                if datetime.utcnow() > user_token.expires_at.replace(tzinfo=None):
                    await user_token.destroy()
                    return None

                encrypted_tokens = json.loads(user_token.tokens)
            except Exception:
                return None
        else:
            try:
                user_doc = self.db.user_tokens.find_one({"user_id": user_id})
                if not user_doc:
                    return None

                if datetime.utcnow() > user_doc["expires_at"]:
                    self.db.user_tokens.delete_one({"user_id": user_id})
                    return None

                encrypted_tokens = user_doc["tokens"]
            except PyMongoError:
                return None

        try:
            return {
                "access_token": self.cipher.decrypt(encrypted_tokens["access_token"].encode()).decode(),
                "refresh_token": self.cipher.decrypt(encrypted_tokens["refresh_token"].encode()).decode(),
                "expires_at": encrypted_tokens["expires_at"],
                "scope": encrypted_tokens["scope"]
            }
        except Exception:
            return None

    async def store_session(self, session_id: str, user_id: str, platform: str):
        """Almacena sesión MCP en MongoDB"""
        session_data = {
            "user_id": user_id,
            "platform": platform,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }

        if self.use_parse:
            try:
                from parse import ParseObject
                UserSession = ParseObject("UserSession")
                user_session = UserSession()
                user_session.session_id = session_id
                user_session.data = json.dumps(session_data)
                await user_session.save()
            except Exception as e:
                raise Exception(f"Parse session storage failed: {str(e)}")
        else:
            try:
                self.db.user_sessions.update_one(
                    {"session_id": session_id},
                    {"$set": session_data},
                    upsert=True
                )
                # Programar eliminación automática
                self.db.user_sessions.create_index("expires_at", expireAfterSeconds=0)
            except PyMongoError as e:
                raise Exception(f"MongoDB session storage failed: {str(e)}")

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Obtiene datos de sesión desde MongoDB"""
        if self.use_parse:
            try:
                from parse import Query
                UserSession = Query("UserSession")
                user_session = await UserSession.get_first(session_id=session_id)

                if not user_session:
                    return None

                if datetime.utcnow() > user_session.expires_at.replace(tzinfo=None):
                    await user_session.destroy()
                    return None

                return json.loads(user_session.data)
            except Exception:
                return None
        else:
            try:
                session_doc = self.db.user_sessions.find_one({"session_id": session_id})
                if not session_doc:
                    return None

                if datetime.utcnow() > session_doc["expires_at"]:
                    self.db.user_sessions.delete_one({"session_id": session_id})
                    return None

                return session_doc
            except PyMongoError:
                return None
