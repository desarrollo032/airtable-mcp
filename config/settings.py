
"""
Configuration Settings for the MCP Server
"""
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server settings
    port: int = int(os.getenv("PORT", 8000))
    host: str = os.getenv("HOST", "0.0.0.0")

    # MCP settings
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "auto")  # stdio, http, sse, auto

    # Airtable OAuth
    airtable_client_id: str = os.getenv("AIRTABLE_CLIENT_ID", "")
    airtable_client_secret: str = os.getenv("AIRTABLE_CLIENT_SECRET", "")
    airtable_redirect_uri: str = os.getenv("AIRTABLE_REDIRECT_URI", "")
    
    # Complete Airtable OAuth Scopes for full functionality
    airtable_scopes: str = (
        "data.records:read "
        "data.records:write "
        "data.recordComments:read "
        "data.recordComments:write "
        "schema.bases:read "
        "schema.bases:write "
        "webhook:manage "
        "block:manage "
        "user.email:read"
    )

    # Database
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    database_url: str = os.getenv("DATABASE_URL", "")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
