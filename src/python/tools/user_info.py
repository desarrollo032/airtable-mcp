"""
User Information Tools for Airtable MCP
Implements user.email:read scope
"""
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class UserInfoTools:
    def __init__(self, airtable_service):
        """Initialize with AirtableService instance"""
        self.service = airtable_service

    async def get_user_info(self, access_token: str) -> str:
        """
        Get current user information including email
        Scope: user.email:read
        """
        try:
            result = await self.service.get_user_info(access_token)
            
            user_id = result.get("id", "unknown")
            email = result.get("email", "unknown")
            first_name = result.get("firstName", "")
            last_name = result.get("lastName", "")
            full_name = f"{first_name} {last_name}".strip()
            profile_url = result.get("profileUrl", "")
            locale = result.get("locale", "unknown")
            time_zone = result.get("timeZone", "unknown")
            created_time = result.get("createdTime", "unknown")
            
            output = [f"User Information"]
            output.append("=" * 50)
            output.append(f"User ID: {user_id}")
            output.append(f"Email: {email}")
            output.append(f"Name: {full_name or 'Not provided'}")
            output.append(f"Profile URL: {profile_url or 'Not provided'}")
            output.append(f"Locale: {locale}")
            output.append(f"Time Zone: {time_zone}")
            output.append(f"Created: {created_time}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return f"Error getting user info: {str(e)}"

    async def get_user_email_only(self, access_token: str) -> str:
        """
        Get only the user's email address
        Scope: user.email:read
        """
        try:
            result = await self.service.get_user_info(access_token)
            email = result.get("email", "unknown")
            return f"User Email: {email}"
            
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return f"Error getting user email: {str(e)}"

    async def get_user_preferences(self, access_token: str) -> str:
        """
        Get user preferences and settings
        Note: This might not be available in all API versions
        Scope: user.email:read
        """
        try:
            result = await self.service.get_user_info(access_token)
            
            # Extract preferences if available
            preferences = result.get("preferences", {})
            if not preferences:
                return "No preferences information available in user data"
            
            output = [f"User Preferences"]
            output.append("=" * 50)
            
            for key, value in preferences.items():
                output.append(f"{key}: {value}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return f"Error getting user preferences: {str(e)}"

    async def get_user_organizations(self, access_token: str) -> str:
        """
        Get organizations/workspaces the user has access to
        Note: This might require additional API calls or permissions
        Scope: user.email:read
        """
        try:
            # This would typically require additional API endpoints
            # For now, we'll return a placeholder message
            return "Organization information requires additional API endpoints not currently available"
            
        except Exception as e:
            logger.error(f"Error getting user organizations: {e}")
            return f"Error getting user organizations: {str(e)}"

    async def verify_user_permissions(self, base_id: str, access_token: str) -> str:
        """
        Verify what permissions the user has for a specific base
        This combines user info with base access verification
        Scope: user.email:read
        """
        try:
            # Get user info first
            user_result = await self.service.get_user_info(access_token)
            user_email = user_result.get("email", "unknown")
            user_id = user_result.get("id", "unknown")
            
            # Try to list bases to verify access
            bases_result = await self.service.list_bases(access_token)
            bases = bases_result.get("bases", [])
            
            # Check if user has access to the specified base
            has_access = False
            user_base = None
            
            for base in bases:
                if base.get("id") == base_id:
                    has_access = True
                    user_base = base
                    break
            
            output = [f"Permission Verification for Base: {base_id}"]
            output.append("=" * 50)
            output.append(f"User Email: {user_email}")
            output.append(f"User ID: {user_id}")
            output.append(f"Has Access: {has_access}")
            
            if user_base:
                base_name = user_base.get("name", "unknown")
                base_role = user_base.get("permissionLevel", "unknown")
                output.append(f"Base Name: {base_name}")
                output.append(f"User Role: {base_role}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error verifying user permissions: {e}")
            return f"Error verifying user permissions: {str(e)}"

# MCP Tool Registration Functions
def register_user_info_tools(mcp, service):
    """Register all user info tools with MCP server"""
    tools = UserInfoTools(service)
    
    @mcp.tool()
    async def get_current_user_info() -> str:
        """Get current user information including email"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_user_info(access_token)

    @mcp.tool()
    async def get_user_email() -> str:
        """Get only the user's email address"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_user_email_only(access_token)

    @mcp.tool()
    async def get_user_settings() -> str:
        """Get user preferences and settings"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_user_preferences(access_token)

    @mcp.tool()
    async def check_base_permissions(base_id: str) -> str:
        """Check user permissions for a specific base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.verify_user_permissions(base_id, access_token)
