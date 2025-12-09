"""
OAuth Routes for Airtable Authentication with Secure Token Storage
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from services.auth_service import AuthService
from services.airtable_service import AirtableService
import secrets
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/airtable/login")
async def airtable_login(
    request: Request,
    user_id: str = Query(..., description="User identifier"),
    platform: str = Query("unknown", description="Platform (chatgpt, mistral, etc.)"),
    conversation_id: str = Query(None, description="Conversation ID"),
    auth_service: AuthService = Depends()
):
    """Inicia flujo OAuth con Airtable"""
    state = secrets.token_urlsafe(16)
    await auth_service.store_oauth_state(user_id, state, platform, conversation_id)

    auth_url = (
        f"https://airtable.com/oauth2/v1/authorize?"
        f"client_id={os.getenv('AIRTABLE_CLIENT_ID')}&"
        f"redirect_uri={os.getenv('AIRTABLE_REDIRECT_URI')}&"
        f"response_type=code&"
        f"scope=data.records:read%20data.records:write%20schema.bases:read&"
        f"state={state}"
    )
    return RedirectResponse(auth_url)

@router.get("/airtable/callback")
async def airtable_callback(
    code: str = Query(...),
    state: str = Query(...),
    auth_service: AuthService = Depends(),
    airtable_service: AirtableService = Depends()
):
    """Callback de OAuth con manejo seguro de tokens"""
    try:
        # Validate OAuth state
        oauth_data = await auth_service.validate_oauth_state(state)
        if not oauth_data:
            logger.warning(f"Invalid OAuth state: {state}")
            raise HTTPException(400, "Invalid or expired OAuth state")

        # Exchange code for tokens
        tokens = await airtable_service.exchange_code_for_tokens(code)
        if not tokens.get("access_token"):
            logger.error("Failed to obtain access token from Airtable")
            raise HTTPException(500, "Failed to obtain access token")

        # Create unique session ID
        session_id = await auth_service.create_session_id()

        # Store tokens securely
        await auth_service.store_airtable_tokens(
            session_id=session_id,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens.get("expires_in", 3600),  # Default 1 hour
            platform=oauth_data.get("platform", "unknown"),
            conversation_id=oauth_data.get("conversation_id")
        )

        logger.info(f"Successfully created session {session_id} for user {oauth_data.get('user_id')}")

        # Return success page with session_id
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Airtable Authentication Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: #28a745; }}
                .session-id {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1 class="success">✅ Authentication Successful!</h1>
            <p>Your Airtable account has been connected successfully.</p>
            <p><strong>Session ID:</strong></p>
            <div class="session-id">{session_id}</div>
            <p>You can now return to your conversation and use Airtable tools.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(500, f"Authentication failed: {str(e)}")

@router.post("/airtable/refresh/{session_id}")
async def refresh_tokens(
    session_id: str,
    auth_service: AuthService = Depends()
):
    """Manually refresh tokens for a session"""
    try:
        new_access_token = await auth_service.refresh_tokens_if_needed(session_id)
        if new_access_token:
            return {"status": "refreshed", "access_token": new_access_token}
        else:
            raise HTTPException(400, "Token refresh failed or not needed")
    except Exception as e:
        logger.error(f"Token refresh error for session {session_id}: {str(e)}")
        raise HTTPException(500, f"Token refresh failed: {str(e)}")
