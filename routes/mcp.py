"""
MCP Protocol Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/capabilities")
async def get_capabilities():
    """Get MCP server capabilities"""
    return {
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": True
            },
            "resources": {
                "listChanged": True
            },
            "prompts": {
                "listChanged": True
            },
            "logging": {},
            "experimental": {
                "toon_support": True,
                "multi_user": True
            }
        },
        "serverInfo": {
            "name": "airtable-mcp",
            "version": "2.0.0"
        }
    }
