"""Health check endpoints."""

from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check that verifies Pixeltable is initialized."""
    import pixeltable as pxt
    
    try:
        # Verify we can list tables (basic operation)
        pxt.list_tables()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}