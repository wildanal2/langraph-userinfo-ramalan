import langwatch
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

def init_langwatch():
    """Initialize LangWatch tracing"""
    if settings.langwatch_enabled and settings.langwatch_api_key:
        try:
            langwatch.api_key = settings.langwatch_api_key
            langwatch.endpoint = settings.langwatch_endpoint
            langwatch.setup()  # Setup auto-instrumentation
            logger.info("LangWatch tracing initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize LangWatch: {e}")
    else:
        logger.info("LangWatch tracing disabled")

def get_langwatch_metadata(session_id: str, user_id: str = None, **kwargs):
    """Get LangWatch metadata for tracing"""
    if not settings.langwatch_enabled:
        return {}
    
    metadata = {
        "session_id": session_id,
        "user_id": user_id or session_id,
        "environment": settings.environment,
        "app_version": settings.app_version,
    }
    metadata.update(kwargs)
    return metadata
