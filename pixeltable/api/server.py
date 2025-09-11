"""Main FastAPI application for Pixeltable API server."""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import pixeltable as pxt
from pixeltable.api import __version__
from pixeltable.api.routers import health, tables, data, auth, media, computed, batch
from pixeltable.api.middleware import AuthenticationMiddleware, RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Pixeltable on startup and cleanup on shutdown."""
    print("Initializing Pixeltable...")
    pxt.init()
    yield
    print("Shutting down Pixeltable API server...")


app = FastAPI(
    title="Pixeltable API",
    description="REST API for Pixeltable - AI Data Infrastructure",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware (optional auth for now)
app.add_middleware(
    AuthenticationMiddleware,
    require_auth=False  # Set to True to require auth for all endpoints
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(tables.router, prefix="/api/v1", tags=["tables"])
app.include_router(data.router, prefix="/api/v1", tags=["data"])
app.include_router(media.router, prefix="/api/v1", tags=["media"])
app.include_router(computed.router, prefix="/api/v1", tags=["computed"])
app.include_router(batch.router, prefix="/api/v1", tags=["batch"])


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Pixeltable API",
        "version": __version__,
        "documentation": "/docs",
        "openapi": "/openapi.json",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )