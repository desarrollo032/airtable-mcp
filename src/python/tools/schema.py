"""
Schema Management Tools for Airtable MCP
Implements schema.bases:read and schema.bases:write scopes
"""
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class SchemaTools:
    def __init__(self, airtable_service):
        """Initialize with AirtableService instance"""
        self.service = airtable_service

    async def get_base_schema(self, base_id: str, access_token: str) -> str:
        """
        Get detailed schema information for a base
        Scope: schema.bases:read
        """
        try:
            result = await self.service.get_base_schema(base_id, access_token)
            tables = result.get("tables", [])
            
            if not tables:
                return f"No tables found in base {base_id}"
            
            output = [f"Schema for Base: {base_id}"]
            output.append("=" * 50)
            
            for i, table in enumerate(tables, 1):
                table_id = table.get("id", "unknown")
                table_name = table.get("name", "unknown")
                description = table.get("description", "")
                
                output.append(f"\nTable {i}: {table_name} (ID: {table_id})")
                if description:
                    output.append(f"Description: {description}")
                
                fields = table.get("fields", [])
                if fields:
                    output.append("Fields:")
                    for field in fields:
                        field_id = field.get("id", "unknown")
                        field_name = field.get("name", "unknown")
                        field_type = field.get("type", "unknown")
                        field_config = field.get("config", {})
                        
                        output.append(f"  - {field_name} (ID: {field_id})")
                        output.append(f"    Type: {field_type}")
                        if field_config:
                            output.append(f"    Config: {json.dumps(field_config, indent=6)}")
                else:
                    output.append("  No fields defined")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting base schema: {e}")
            return f"Error getting base schema: {str(e)}"

    async def create_field(self, base_id: str, table_name: str, field_name: str, field_type: str, field_config: str = "{}", access_token: str = "") -> str:
        """
        Create a new field in a table
        Scope: schema.bases:write
        """
        try:
            # Parse field config
            try:
                config_dict = json.loads(field_config) if field_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in field_config"
            
            # Get table ID first
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            # Create field config
            field_config_dict = {
                "name": field_name,
                "type": field_type
            }
            field_config_dict.update(config_dict)
            
            result = await self.service.create_field(
                base_id=base_id,
                table_id=table_id,
                field_config=field_config_dict,
                access_token=access_token
            )
            
            fields = result.get("fields", [])
            if fields:
                field = fields[0]
                field_id = field.get("id", "unknown")
                return f"Successfully created field '{field_name}' with ID: {field_id}"
            else:
                return "Field created but no field data returned"
            
        except Exception as e:
            logger.error(f"Error creating field: {e}")
            return f"Error creating field: {str(e)}"

    async def update_field(self, base_id: str, table_name: str, field_id: str, field_name: str = None, field_config: str = "{}", access_token: str = "") -> str:
        """
        Update an existing field in a table
        Scope: schema.bases:write
        """
        try:
            # Parse field config
            try:
                config_dict = json.loads(field_config) if field_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in field_config"
            
            # Get table ID first
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            # Build update config
            update_config = {}
            if field_name:
                update_config["name"] = field_name
            update_config.update(config_dict)
            
            result = await self.service.update_field(
                base_id=base_id,
                table_id=table_id,
                field_id=field_id,
                field_config=update_config,
                access_token=access_token
            )
            
            field = result.get("field", {})
            updated_name = field.get("name", field_name or "unknown")
            return f"Successfully updated field '{updated_name}' (ID: {field_id})"
            
        except Exception as e:
            logger.error(f"Error updating field: {e}")
            return f"Error updating field: {str(e)}"

    async def delete_field(self, base_id: str, table_name: str, field_id: str, access_token: str = "") -> str:
        """
        Delete a field from a table
        Scope: schema.bases:write
        """
        try:
            # Get table ID first
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            result = await self.service.delete_field(
                base_id=base_id,
                table_id=table_id,
                field_id=field_id,
                access_token=access_token
            )
            
            return f"Successfully deleted field {field_id} from table '{table_name}'"
            
        except Exception as e:
            logger.error(f"Error deleting field: {e}")
            return f"Error deleting field: {str(e)}"

    async def create_table(self, base_id: str, table_name: str, table_config: str = "{}", access_token: str = "") -> str:
        """
        Create a new table in a base
        Scope: schema.bases:write
        """
        try:
            # Parse table config
            try:
                config_dict = json.loads(table_config) if table_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in table_config"
            
            # Build table config
            table_config_dict = {
                "name": table_name,
                "description": config_dict.get("description", ""),
                "fields": config_dict.get("fields", [])
            }
            
            result = await self.service.create_table(
                base_id=base_id,
                table_config=table_config_dict,
                access_token=access_token
            )
            
            table = result.get("table", {})
            table_id = table.get("id", "unknown")
            return f"Successfully created table '{table_name}' with ID: {table_id}"
            
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return f"Error creating table: {str(e)}"

    async def update_table(self, base_id: str, table_name: str, new_table_name: str = None, table_config: str = "{}", access_token: str = "") -> str:
        """
        Update an existing table in a base
        Scope: schema.bases:write
        """
        try:
            # Parse table config
            try:
                config_dict = json.loads(table_config) if table_config else {}
            except json.JSONDecodeError:
                return "Error: Invalid JSON in table_config"
            
            # Get table ID first
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            # Build update config
            update_config = {}
            if new_table_name:
                update_config["name"] = new_table_name
            if "description" in config_dict:
                update_config["description"] = config_dict["description"]
            
            result = await self.service.update_table(
                base_id=base_id,
                table_id=table_id,
                table_config=update_config,
                access_token=access_token
            )
            
            table = result.get("table", {})
            updated_name = table.get("name", new_table_name or table_name)
            return f"Successfully updated table '{updated_name}' (ID: {table_id})"
            
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            return f"Error updating table: {str(e)}"

    async def delete_table(self, base_id: str, table_name: str, access_token: str = "") -> str:
        """
        Delete a table from a base
        Scope: schema.bases:write
        """
        try:
            # Get table ID first
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            result = await self.service.delete_table(
                base_id=base_id,
                table_id=table_id,
                access_token=access_token
            )
            
            return f"Successfully deleted table '{table_name}'"
            
        except Exception as e:
            logger.error(f"Error deleting table: {e}")
            return f"Error deleting table: {str(e)}"

# MCP Tool Registration Functions
def register_schema_tools(mcp, service):
    """Register all schema tools with MCP server"""
    tools = SchemaTools(service)
    
    @mcp.tool()
    async def get_base_schema_detailed(base_id: str) -> str:
        """Get detailed schema information for a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_base_schema(base_id, access_token)

    @mcp.tool()
    async def create_table_field(base_id: str, table_name: str, field_name: str, field_type: str, field_config: str = "{}") -> str:
        """Create a new field in a table"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.create_field(base_id, table_name, field_name, field_type, field_config, access_token)

    @mcp.tool()
    async def update_table_field(base_id: str, table_name: str, field_id: str, field_name: str = None, field_config: str = "{}") -> str:
        """Update an existing field in a table"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.update_field(base_id, table_name, field_id, field_name, field_config, access_token)

    @mcp.tool()
    async def delete_table_field(base_id: str, table_name: str, field_id: str) -> str:
        """Delete a field from a table"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.delete_field(base_id, table_name, field_id, access_token)

    @mcp.tool()
    async def create_new_table(base_id: str, table_name: str, table_config: str = "{}") -> str:
        """Create a new table in a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.create_table(base_id, table_name, table_config, access_token)

    @mcp.tool()
    async def update_existing_table(base_id: str, table_name: str, new_table_name: str = None, table_config: str = "{}") -> str:
        """Update an existing table in a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.update_table(base_id, table_name, new_table_name, table_config, access_token)

    @mcp.tool()
    async def delete_existing_table(base_id: str, table_name: str) -> str:
        """Delete a table from a base"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.delete_table(base_id, table_name, access_token)
