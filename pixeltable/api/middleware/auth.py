"""Authentication middleware for Pixeltable API."""

from typing import Optional, Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

from pixeltable.api.models.auth import AuthContext, verify_api_key_auth
from pixeltable.api.routers.auth import api_usage_store

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for API authentication and usage tracking."""
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None,
        require_auth: bool = False
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/docs",
            "/openapi.json",
            "/api/v1/health",
            "/api/v1/ready",
            "/api/v1/auth/api-keys",  # Allow creating first API key
        ]
        self.require_auth = require_auth
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and track API usage."""
        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Extract API key from headers
        api_key = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
        elif request.headers.get("X-API-Key"):
            api_key = request.headers.get("X-API-Key")
        
        # Track request timing
        start_time = time.time()
        
        # Store auth context in request state for use in endpoints
        if api_key:
            try:
                # This would normally call the verify function
                # For now, we'll skip actual verification in middleware
                # The endpoints will handle it via Depends
                request.state.api_key = api_key
            except Exception as e:
                logger.error(f"Auth verification failed: {e}")
                if self.require_auth:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid API key"}
                    )
        elif self.require_auth:
            return JSONResponse(
                status_code=401,
                content={"detail": "API key required"}
            )
        
        # Process the request
        response = await call_next(request)
        
        # Track API usage
        if hasattr(request.state, "auth_context"):
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Record usage (simplified for demo)
            auth_context: AuthContext = request.state.auth_context
            if auth_context.api_key_id not in api_usage_store:
                api_usage_store[auth_context.api_key_id] = []
            
            api_usage_store[auth_context.api_key_id].append({
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "response_time_ms": elapsed_time,
                "timestamp": time.time()
            })
        
        return response