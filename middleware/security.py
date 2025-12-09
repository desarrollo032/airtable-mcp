"""
Security Middleware for FastAPI
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_requests=100, rate_limit_window=60):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]

        if len(self.requests[client_ip]) >= self.rate_limit_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )

        self.requests[client_ip].append(current_time)

        # Security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

# Factory function for dependency injection
def security_middleware(app):
    return SecurityMiddleware(app)
