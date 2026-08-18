"""
Advanced Webhooks Tools for Airtable MCP
Implements webhook:manage scope with comprehensive webhook operations
"""
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class WebhooksAdvancedTools:
    def __init__(self, airtable_service):
        """Initialize with AirtableService instance"""
        self.service = airtable_service

    async def list_webhooks(self, base_id: str, access_token: str) -> str:
        """
        List all webhooks for a base
        Scope: webhook:manage
        """
        try:
            result = await self.service.list_webhooks(base_id, access_token)
            webhooks = result.get("webhooks", [])
            
            if not webhooks:
                return f"No webhooks found for base {base_id}"
            
            output = [f"Webhooks for Base: {base_id}"]
            output.append("=" * 50)
            
            for i, webhook in enumerate(webhooks, 1):
                webhook_id = webhook.get("id", "unknown")
                notification_url = webhook.get("notificationUrl", "unknown")
                expiration_time = webhook.get("expirationTime", "unknown")
                last_success_time = webhook.get("lastSuccessTime", "never")
                last_failure_time = webhook.get("lastFailureTime", "never")
                status = webhook.get("status", "unknown")
                
                output.append(f"\nWebhook {i}:")
                output.append(f"  ID: {webhook_id}")
                output.append(f"  URL: {notification_url}")
                output.append(f"  Status: {status}")
                output.append(f"  Expires: {expiration_time}")
                output.append(f"  Last Success: {last_success_time}")
                output.append(f"  Last Failure: {last_failure_time}")
                
                # Show specification if available
                spec = webhook.get("specification", {})
                if spec:
                    output.append(f"  Specification:")
                    output.append(f"    Options: {json.dumps(spec.get('options', {}), indent=6)}")
                    output.append(f"    Filters: {json.dumps(spec.get('filters', {}), indent=6)}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error listing webhooks: {e}")
            return f"Error listing webhooks: {str(e)}"

    async def create_webhook(self, base_id: str, notification_url: str, webhook_config: str = "{}", access_token: str = "") -> str:
        """
        Create a new webhook for a base
        Scope: webhook:manage
        """
        try:
            # Parse webhook config
            try:
                config_dict = json.loads(webhook_config) if webhook_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in webhook_config"
            
            # Build webhook config
            webhook_config_dict = {
                "notificationUrl": notification_url,
                "specification": {
                    "options": {
                        "filters": {
                            "data": config_dict.get("filters", {}),
                            "timeZone": config_dict.get("timeZone", "UTC"),
                            "includeHeaders": config_dict.get("includeHeaders", False),
                            "includePayload": config_dict.get("includePayload", True)
                        }
                    }
                }
            }
            
            result = await self.service.create_webhook(
                base_id=base_id,
                webhook_config=webhook_config_dict,
                access_token=access_token
            )
            
            webhook = result.get("webhook", {})
            webhook_id = webhook.get("id", "unknown")
            expiration_time = webhook.get("expirationTime", "unknown")
            
            return f"Successfully created webhook with ID: {webhook_id}\nExpires: {expiration_time}\nURL: {notification_url}"
            
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return f"Error creating webhook: {str(e)}"

    async def delete_webhook(self, base_id: str, webhook_id: str, access_token: str = "") -> str:
        """
        Delete a webhook from a base
        Scope: webhook:manage
        """
        try:
            result = await self.service.delete_webhook(
                base_id=base_id,
                webhook_id=webhook_id,
                access_token=access_token
            )
            
            return f"Successfully deleted webhook {webhook_id}"
            
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return f"Error deleting webhook: {str(e)}"

    async def get_webhook_payloads(self, base_id: str, webhook_id: str, access_token: str = "") -> str:
        """
        Get webhook payloads for debugging
        Scope: webhook:manage
        """
        try:
            result = await self.service.get_webhook_payloads(
                base_id=base_id,
                webhook_id=webhook_id,
                access_token=access_token
            )
            
            payloads = result.get("payloads", [])
            if not payloads:
                return f"No payloads found for webhook {webhook_id}"
            
            output = [f"Webhook Payloads for: {webhook_id}"]
            output.append("=" * 50)
            
            for i, payload in enumerate(payloads, 1):
                timestamp = payload.get("timestamp", "unknown")
                hook_id = payload.get("hookId", "unknown")
                payload_data = payload.get("payload", {})
                
                output.append(f"\nPayload {i}:")
                output.append(f"  Timestamp: {timestamp}")
                output.append(f"  Hook ID: {hook_id}")
                output.append(f"  Data: {json.dumps(payload_data, indent=6)}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting webhook payloads: {e}")
            return f"Error getting webhook payloads: {str(e)}"

    async def refresh_webhook(self, base_id: str, webhook_id: str, access_token: str = "") -> str:
        """
        Refresh webhook expiration
        Scope: webhook:manage
        """
        try:
            result = await self.service.refresh_webhook(
                base_id=base_id,
                webhook_id=webhook_id,
                access_token=access_token
            )
            
            webhook = result.get("webhook", {})
            expiration_time = webhook.get("expirationTime", "unknown")
            
            return f"Successfully refreshed webhook {webhook_id}\nNew expiration: {expiration_time}"
            
        except Exception as e:
            logger.error(f"Error refreshing webhook: {e}")
            return f"Error refreshing webhook: {str(e)}"

    async def get_webhook_details(self, base_id: str, webhook_id: str, access_token: str = "") -> str:
        """
        Get detailed information about a specific webhook
        Scope: webhook:manage
        """
        try:
            # List all webhooks and find the specific one
            result = await self.service.list_webhooks(base_id, access_token)
            webhooks = result.get("webhooks", [])
            
            webhook = None
            for w in webhooks:
                if w.get("id") == webhook_id:
                    webhook = w
                    break
            
            if not webhook:
                return f"Webhook {webhook_id} not found in base {base_id}"
            
            output = [f"Webhook Details: {webhook_id}"]
            output.append("=" * 50)
            
            notification_url = webhook.get("notificationUrl", "unknown")
            expiration_time = webhook.get("expirationTime", "unknown")
            last_success_time = webhook.get("lastSuccessTime", "never")
            last_failure_time = webhook.get("lastFailureTime", "never")
            status = webhook.get("status", "unknown")
            
            output.append(f"URL: {notification_url}")
            output.append(f"Status: {status}")
            output.append(f"Expires: {expiration_time}")
            output.append(f"Last Success: {last_success_time}")
            output.append(f"Last Failure: {last_failure_time}")
            
            # Show specification in detail
            spec = webhook.get("specification", {})
            if spec:
                output.append(f"\nSpecification:")
                options = spec.get("options", {})
                filters = options.get("filters", {})
                
                output.append(f"  Time Zone: {filters.get('timeZone', 'UTC')}")
                output.append(f"  Include Headers: {filters.get('includeHeaders', False)}")
                output.append(f"  Include Payload: {filters.get('includePayload', True)}")
                output.append(f"  Data Filters: {json.dumps(filters.get('data', {}), indent=6)}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting webhook details: {e}")
            return f"Error getting webhook details: {str(e)}"

# MCP Tool Registration Functions
def register_webhook_tools_advanced(mcp, service):
    """Register all advanced webhook tools with MCP server"""
    tools = WebhooksAdvancedTools(service)
    
    @mcp.tool()
    async def list_all_webhooks(base_id: str) -> str:
        """List all webhooks for a base with detailed information"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.list_webhooks(base_id, access_token)

    @mcp.tool()
    async def create_new_webhook(base_id: str, notification_url: str, webhook_config: str = "{}") -> str:
        """Create a new webhook for a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.create_webhook(base_id, notification_url, webhook_config, access_token)

    @mcp.tool()
    async def delete_webhook_by_id(base_id: str, webhook_id: str) -> str:
        """Delete a webhook from a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.delete_webhook(base_id, webhook_id, access_token)

    @mcp.tool()
    async def get_webhook_debug_payloads(base_id: str, webhook_id: str) -> str:
        """Get webhook payloads for debugging"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_webhook_payloads(base_id, webhook_id, access_token)

    @mcp.tool()
    async def refresh_webhook_expiration(base_id: str, webhook_id: str) -> str:
        """Refresh webhook expiration"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.refresh_webhook(base_id, webhook_id, access_token)

    @mcp.tool()
    async def get_webhook_detailed_info(base_id: str, webhook_id: str) -> str:
        """Get detailed information about a specific webhook"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_webhook_details(base_id, webhook_id, access_token)
