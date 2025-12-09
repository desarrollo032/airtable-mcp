"""
Health Check Routes
"""
from fastapi import APIRouter
from services.airtable_service import AirtableService
from services.auth_service import AuthService

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "airtable-mcp"}

@router.get("/detailed")
async def detailed_health_check(
    airtable_service: AirtableService,
    auth_service: AuthService
):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "service": "airtable-mcp",
        "version": "2.0.0",
        "features": {
            "toon_support": True,
            "oauth": True,
            "multi_user": True,
            "mcp_transport": ["stdio", "http", "sse"]
        },
        "dependencies": {}
    }

    # Check Redis connection
    try:
        await auth_service.redis.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
