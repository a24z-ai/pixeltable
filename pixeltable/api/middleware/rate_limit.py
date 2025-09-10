"""Rate limiting middleware for Pixeltable API."""

from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

from pixeltable.api.models.auth import RateLimitConfig

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self) -> Tuple[bool, Dict[str, any]]:
        """Check if request is allowed under rate limit."""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on time elapsed
            time_elapsed = now - self.last_refill
            tokens_to_add = time_elapsed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have tokens available
            if self.tokens >= 1:
                self.tokens -= 1
                return True, {
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": str(int(self.tokens)),
                    "X-RateLimit-Reset": str(int(now + 60))
                }
            else:
                # Calculate when next token will be available
                tokens_needed = 1 - self.tokens
                seconds_until_token = tokens_needed / (self.requests_per_minute / 60.0)
                reset_time = int(now + seconds_until_token)
                
                return False, {
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(int(seconds_until_token))
                }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(
        self,
        app: ASGIApp,
        default_config: Optional[RateLimitConfig] = None,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.default_config = default_config or RateLimitConfig()
        self.exclude_paths = exclude_paths or [
            "/",
            "/docs",
            "/openapi.json",
            "/api/v1/health",
            "/api/v1/ready",
        ]
        # Store rate limiters per API key or IP
        self.limiters: Dict[str, RateLimiter] = {}
        # Cleanup old limiters periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour
    
    def get_client_id(self, request: Request) -> str:
        """Get a unique identifier for the client."""
        # Try to get API key first
        if hasattr(request.state, "api_key"):
            return f"key:{request.state.api_key}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def cleanup_limiters(self):
        """Remove old rate limiters to prevent memory leaks."""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            # Remove limiters that haven't been used in the last hour
            cutoff_time = now - 3600
            to_remove = []
            for client_id, limiter in self.limiters.items():
                if limiter.last_refill < cutoff_time:
                    to_remove.append(client_id)
            
            for client_id in to_remove:
                del self.limiters[client_id]
            
            self.last_cleanup = now
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} inactive rate limiters")
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to the request."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Periodic cleanup
        await self.cleanup_limiters()
        
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Get or create rate limiter for this client
        if client_id not in self.limiters:
            # Get rate limit config from auth context if available
            config = self.default_config
            if hasattr(request.state, "auth_context"):
                config = request.state.auth_context.rate_limit
            
            self.limiters[client_id] = RateLimiter(
                requests_per_minute=config.requests_per_minute,
                burst_size=config.burst_size
            )
        
        limiter = self.limiters[client_id]
        
        # Check rate limit
        allowed, headers = await limiter.is_allowed()
        
        if not allowed:
            # Rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers=headers
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response


class SlidingWindowRateLimiter:
    """Alternative sliding window rate limiter implementation."""
    
    def __init__(self, requests_per_hour: int = 1000):
        self.requests_per_hour = requests_per_hour
        self.window_size = 3600  # 1 hour in seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed under hourly rate limit."""
        async with self.lock:
            now = time.time()
            
            # Remove requests outside the sliding window
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # Check if we're under the limit
            if len(self.requests) < self.requests_per_hour:
                self.requests.append(now)
                return True
            
            return False