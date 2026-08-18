"""
Blocks Tools for Airtable MCP
Implements block:manage scope for Blocks CLI operations
"""
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class BlocksTools:
    def __init__(self, airtable_service):
        """Initialize with AirtableService instance"""
        self.service = airtable_service

    async def list_blocks(self, access_token: str) -> str:
        """
        List all blocks for the user
        Scope: block:manage
        """
        try:
            result = await self.service.list_blocks(access_token)
            blocks = result.get("blocks", [])
            
            if not blocks:
                return "No blocks found for this user"
            
            output = [f"User Blocks"]
            output.append("=" * 50)
            
            for i, block in enumerate(blocks, 1):
                block_id = block.get("id", "unknown")
                block_name = block.get("name", "unknown")
                block_type = block.get("type", "unknown")
                description = block.get("description", "")
                status = block.get("status", "unknown")
                version = block.get("version", "unknown")
                created_time = block.get("createdTime", "unknown")
                updated_time = block.get("updatedTime", "unknown")
                
                output.append(f"\nBlock {i}:")
                output.append(f"  ID: {block_id}")
                output.append(f"  Name: {block_name}")
                output.append(f"  Type: {block_type}")
                output.append(f"  Status: {status}")
                output.append(f"  Version: {version}")
                if description:
                    output.append(f"  Description: {description}")
                output.append(f"  Created: {created_time}")
                output.append(f"  Updated: {updated_time}")
                
                # Show configuration if available
                config = block.get("config", {})
                if config:
                    output.append(f"  Config: {json.dumps(config, indent=6)}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error listing blocks: {e}")
            return f"Error listing blocks: {str(e)}"

    async def get_block_info(self, block_id: str, access_token: str) -> str:
        """
        Get detailed information about a specific block
        Scope: block:manage
        """
        try:
            result = await self.service.get_block_info(block_id, access_token)
            
            block_name = result.get("name", "unknown")
            block_type = result.get("type", "unknown")
            description = result.get("description", "")
            status = result.get("status", "unknown")
            version = result.get("version", "unknown")
            created_time = result.get("createdTime", "unknown")
            updated_time = result.get("updatedTime", "unknown")
            author = result.get("author", {})
            
            output = [f"Block Details: {block_name}"]
            output.append("=" * 50)
            output.append(f"Block ID: {block_id}")
            output.append(f"Type: {block_type}")
            output.append(f"Status: {status}")
            output.append(f"Version: {version}")
            if description:
                output.append(f"Description: {description}")
            
            if author:
                author_name = author.get("name", "unknown")
                author_email = author.get("email", "unknown")
                output.append(f"Author: {author_name} ({author_email})")
            
            output.append(f"Created: {created_time}")
            output.append(f"Updated: {updated_time}")
            
            # Show detailed configuration
            config = result.get("config", {})
            if config:
                output.append(f"\nConfiguration:")
                output.append(json.dumps(config, indent=6))
            
            # Show metadata
            metadata = result.get("metadata", {})
            if metadata:
                output.append(f"\nMetadata:")
                output.append(json.dumps(metadata, indent=6))
            
            # Show permissions
            permissions = result.get("permissions", [])
            if permissions:
                output.append(f"\nPermissions:")
                for permission in permissions:
                    output.append(f"  - {permission}")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting block info: {e}")
            return f"Error getting block info: {str(e)}"

    async def create_block(self, block_config: str, access_token: str = "") -> str:
        """
        Create a new block
        Scope: block:manage
        """
        try:
            # Parse block config
            try:
                config_dict = json.loads(block_config) if block_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in block_config"
            
            # Validate required fields
            if "name" not in config_dict:
                return "Error: 'name' is required in block_config"
            if "type" not in config_dict:
                return "Error: 'type' is required in block_config"
            
            result = await self.service.create_block(
                block_config=config_dict,
                access_token=access_token
            )
            
            block = result.get("block", {})
            block_id = block.get("id", "unknown")
            block_name = block.get("name", "unknown")
            version = block.get("version", "unknown")
            status = block.get("status", "unknown")
            
            return f"Successfully created block '{block_name}'\nBlock ID: {block_id}\nVersion: {version}\nStatus: {status}"
            
        except Exception as e:
            logger.error(f"Error creating block: {e}")
            return f"Error creating block: {str(e)}"

    async def update_block(self, block_id: str, block_config: str, access_token: str = "") -> str:
        """
        Update an existing block
        Scope: block:manage
        """
        try:
            # Parse block config
            try:
                config_dict = json.loads(block_config) if block_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in block_config"
            
            result = await self.service.update_block(
                block_id=block_id,
                block_config=config_dict,
                access_token=access_token
            )
            
            block = result.get("block", {})
            block_name = block.get("name", "unknown")
            version = block.get("version", "unknown")
            status = block.get("status", "unknown")
            
            return f"Successfully updated block '{block_name}'\nBlock ID: {block_id}\nVersion: {version}\nStatus: {status}"
            
        except Exception as e:
            logger.error(f"Error updating block: {e}")
            return f"Error updating block: {str(e)}"

    async def delete_block(self, block_id: str, access_token: str = "") -> str:
        """
        Delete a block
        Scope: block:manage
        """
        try:
            result = await self.service.delete_block(
                block_id=block_id,
                access_token=access_token
            )
            
            return f"Successfully deleted block {block_id}"
            
        except Exception as e:
            logger.error(f"Error deleting block: {e}")
            return f"Error deleting block: {str(e)}"

    async def get_block_versions(self, block_id: str, access_token: str) -> str:
        """
        Get version history for a block
        Scope: block:manage
        """
        try:
            # This would typically require a specific API endpoint
            # For now, we'll get the block info and show available version info
            result = await self.service.get_block_info(block_id, access_token)
            
            block_name = result.get("name", "unknown")
            current_version = result.get("version", "unknown")
            
            output = [f"Block Versions: {block_name}"]
            output.append("=" * 50)
            output.append(f"Current Version: {current_version}")
            output.append("Note: Detailed version history requires additional API endpoints")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting block versions: {e}")
            return f"Error getting block versions: {str(e)}"

    async def validate_block_config(self, block_config: str) -> str:
        """
        Validate block configuration without creating the block
        This is a helper function for block creation
        Scope: block:manage
        """
        try:
            # Parse block config
            try:
                config_dict = json.loads(block_config) if block_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in block_config"
            
            output = [f"Block Configuration Validation"]
            output.append("=" * 50)
            
            # Check required fields
            required_fields = ["name", "type"]
            missing_fields = []
            
            for field in required_fields:
                if field not in config_dict:
                    missing_fields.append(field)
            
            if missing_fields:
                output.append(f"❌ Missing required fields: {', '.join(missing_fields)}")
            else:
                output.append("✅ All required fields present")
            
            # Validate field types and values
            if "name" in config_dict:
                name = config_dict["name"]
                if isinstance(name, str) and len(name) > 0:
                    output.append(f"✅ Name: '{name}' (valid)")
                else:
                    output.append(f"❌ Name must be a non-empty string")
            
            if "type" in config_dict:
                valid_types = ["custom", "visualization", "automation", "integration"]
                block_type = config_dict["type"]
                if block_type in valid_types:
                    output.append(f"✅ Type: '{block_type}' (valid)")
                else:
                    output.append(f"❌ Type must be one of: {', '.join(valid_types)}")
            
            # Check optional fields
            optional_fields = ["description", "version", "config", "metadata"]
            for field in optional_fields:
                if field in config_dict:
                    output.append(f"✅ Optional field '{field}' present")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error validating block config: {e}")
            return f"Error validating block config: {str(e)}"

# MCP Tool Registration Functions
def register_blocks_tools(mcp, service):
    """Register all blocks tools with MCP server"""
    tools = BlocksTools(service)
    
    @mcp.tool()
    async def list_all_blocks() -> str:
        """List all blocks for the current user"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.list_blocks(access_token)

    @mcp.tool()
    async def get_block_details(block_id: str) -> str:
        """Get detailed information about a specific block"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_block_info(block_id, access_token)

    @mcp.tool()
    async def create_new_block(block_config: str) -> str:
        """Create a new block with configuration"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.create_block(block_config, access_token)

    @mcp.tool()
    async def update_existing_block(block_id: str, block_config: str) -> str:
        """Update an existing block"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.update_block(block_id, block_config, access_token)

    @mcp.tool()
    async def delete_block_by_id(block_id: str) -> str:
        """Delete a block"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.delete_block(block_id, access_token)

    @mcp.tool()
    async def validate_block_configuration(block_config: str) -> str:
        """Validate block configuration before creation"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.validate_block_config(block_config)

    @mcp.tool()
    async def get_block_version_history(block_id: str) -> str:
        """Get version history for a block"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_block_versions(block_id, access_token)
