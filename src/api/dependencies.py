from fastapi import Header, HTTPException, status
from src.core.config import settings

async def verify_content_length(content_length: int = Header(None)):
    if content_length and content_length > settings.max_request_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Request too large"
        )
