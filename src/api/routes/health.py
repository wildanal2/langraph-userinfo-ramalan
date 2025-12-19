from fastapi import APIRouter
from src.models.schemas import HealthResponse
from src.infrastructure.redis import redis_client
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    redis_status = redis_client.health_check()
    
    return HealthResponse(
        status="healthy" if redis_status else "degraded",
        version=settings.app_version,
        dependencies={
            "redis": "connected" if redis_status else "disconnected",
            "bedrock": "configured"
        }
    )
