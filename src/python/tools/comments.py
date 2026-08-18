"""
Record Comments Tools for Airtable MCP
Implements data.recordComments:read and data.recordComments:write scopes
"""
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class CommentsTools:
    def __init__(self, airtable_service):
        """Initialize with AirtableService instance"""
        self.service = airtable_service

    async def get_record_comments(self, base_id: str, table_id: str, record_id: str, access_token: str) -> str:
        """
        Get comments for a specific record
        Scope: data.recordComments:read
        """
        try:
            result = await self.service.get_record_comments(
                base_id=base_id,
                table_id=table_id,
                record_id=record_id,
                access_token=access_token
            )
            
            comments = result.get("comments", [])
            if not comments:
                return "No comments found for this record."
            
            output = []
            for comment in comments:
                comment_id = comment.get("id", "unknown")
                text = comment.get("text", "")
                author = comment.get("createdBy", {}).get("email", "Unknown")
                created_time = comment.get("createdTime", "Unknown")
                
                output.append(f"Comment ID: {comment_id}")
                output.append(f"Author: {author}")
                output.append(f"Created: {created_time}")
                output.append(f"Text: {text}")
                output.append("-" * 50)
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error getting record comments: {e}")
            return f"Error getting record comments: {str(e)}"

    async def create_record_comment(self, base_id: str, table_id: str, record_id: str, text: str, access_token: str) -> str:
        """
        Create a new comment on a record
        Scope: data.recordComments:write
        """
        try:
            result = await self.service.create_record_comment(
                base_id=base_id,
                table_id=table_id,
                record_id=record_id,
                text=text,
                access_token=access_token
            )
            
            comment = result.get("comment", {})
            comment_id = comment.get("id", "unknown")
            created_time = comment.get("createdTime", "Unknown")
            
            return f"Successfully created comment with ID: {comment_id} at {created_time}"
            
        except Exception as e:
            logger.error(f"Error creating record comment: {e}")
            return f"Error creating record comment: {str(e)}"

    async def update_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str, text: str, access_token: str) -> str:
        """
        Update an existing comment on a record
        Scope: data.recordComments:write
        """
        try:
            result = await self.service.update_record_comment(
                base_id=base_id,
                table_id=table_id,
                record_id=record_id,
                comment_id=comment_id,
                text=text,
                access_token=access_token
            )
            
            comment = result.get("comment", {})
            updated_time = comment.get("lastModifiedTime", "Unknown")
            
            return f"Successfully updated comment {comment_id} at {updated_time}"
            
        except Exception as e:
            logger.error(f"Error updating record comment: {e}")
            return f"Error updating record comment: {str(e)}"

    async def delete_record_comment(self, base_id: str, table_id: str, record_id: str, comment_id: str, access_token: str) -> str:
        """
        Delete a comment from a record
        Scope: data.recordComments:write
        """
        try:
            result = await self.service.delete_record_comment(
                base_id=base_id,
                table_id=table_id,
                record_id=record_id,
                comment_id=comment_id,
                access_token=access_token
            )
            
            return f"Successfully deleted comment {comment_id}"
            
        except Exception as e:
            logger.error(f"Error deleting record comment: {e}")
            return f"Error deleting record comment: {str(e)}"

    async def get_all_comments_for_record(self, base_id: str, table_name: str, record_id: str, access_token: str) -> str:
        """
        Get all comments for a record using table name instead of table ID
        This is a convenience method that first gets the table schema
        """
        try:
            # First get the table schema to find the table ID
            schema_result = await self.service.get_base_schema(base_id, access_token)
            tables = schema_result.get("tables", [])
            
            table_id = None
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("id")
                    break
            
            if not table_id:
                return f"Table '{table_name}' not found in base {base_id}"
            
            return await self.get_record_comments(base_id, table_id, record_id, access_token)
            
        except Exception as e:
            logger.error(f"Error getting comments by table name: {e}")
            return f"Error getting comments by table name: {str(e)}"

# MCP Tool Registration Functions
def register_comment_tools(mcp, service):
    """Register all comment tools with MCP server"""
    tools = CommentsTools(service)
    
    @mcp.tool()
    async def get_record_comments_by_id(base_id: str, table_name: str, record_id: str) -> str:
        """Get comments for a record using base ID, table name, and record ID"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        return await tools.get_all_comments_for_record(base_id, table_name, record_id, access_token)

    @mcp.tool()
    async def create_record_comment_by_id(base_id: str, table_name: str, record_id: str, comment_text: str) -> str:
        """Create a comment on a record using base ID, table name, and record ID"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        
        # Get table ID first
        schema_result = await service.get_base_schema(base_id, access_token)
        tables = schema_result.get("tables", [])
        
        table_id = None
        for table in tables:
            if table.get("name") == table_name:
                table_id = table.get("id")
                break
        
        if not table_id:
            return f"Table '{table_name}' not found in base {base_id}"
        
        return await tools.create_record_comment(base_id, table_id, record_id, comment_text, access_token)

    @mcp.tool()
    async def update_record_comment_by_id(base_id: str, table_name: str, record_id: str, comment_id: str, comment_text: str) -> str:
        """Update a comment on a record"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        
        # Get table ID first
        schema_result = await service.get_base_schema(base_id, access_token)
        tables = schema_result.get("tables", [])
        
        table_id = None
        for table in tables:
            if table.get("name") == table_name:
                table_id = table.get("id")
                break
        
        if not table_id:
            return f"Table '{table_name}' not found in base {base_id}"
        
        return await tools.update_record_comment(base_id, table_id, record_id, comment_id, comment_text, access_token)

    @mcp.tool()
    async def delete_record_comment_by_id(base_id: str, table_name: str, record_id: str, comment_id: str) -> str:
        """Delete a comment from a record"""
        access_token = getattr(mcp, '_access_token', '')
        if not access_token:
            return "Error: No access token available"
        
        # Get table ID first
        schema_result = await service.get_base_schema(base_id, access_token)
        tables = schema_result.get("tables", [])
        
        table_id = None
        for table in tables:
            if table.get("name") == table_name:
                table_id = table.get("id")
                break
        
        if not table_id:
            return f"Table '{table_name}' not found in base {base_id}"
        
        return await tools.delete_record_comment(base_id, table_id, record_id, comment_id, access_token)
