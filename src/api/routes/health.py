"""Health check endpoints"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from ...core.config import get_settings, Settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint"""
    return {"status": "live"}
