"""
User Connections Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from services.auth_service import AuthService
from services.token_storage import TokenStorage

router = APIRouter()

@router.get("/{user_id}/status")
async def get_connection_status(
    user_id: str,
    auth_service: AuthService = Depends(),
    token_storage: TokenStorage = Depends()
):
    """Get connection status for user"""
    tokens = await token_storage.get_tokens(user_id)
    if not tokens:
        return {"connected": False}

    # Check if tokens are still valid
    # Implementation depends on token expiration logic
    return {
        "connected": True,
        "has_refresh_token": bool(tokens.get("refresh_token")),
        "expires_at": tokens.get("expires_at")
    }

@router.delete("/{user_id}/disconnect")
async def disconnect_user(
    user_id: str,
    token_storage: TokenStorage = Depends()
):
    """Disconnect user by removing tokens"""
    await token_storage.delete_tokens(user_id)
    return {"status": "disconnected"}
