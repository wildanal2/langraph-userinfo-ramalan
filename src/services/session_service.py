from typing import Optional
from src.infrastructure.redis import redis_client
from src.core.logging import get_logger

logger = get_logger(__name__)

class SessionService:
    def __init__(self):
        self.redis = redis_client
    
    async def set_returning_flag(self, session_id: str, is_returning: bool):
        """Set flag untuk menandai apakah user returning atau tidak"""
        # Using the .set method we just created in RedisClient
        await self.redis.set(
            f"returning:{session_id}", 
            "1" if is_returning else "0",
            expire=600  # 5 minutes TTL
        )
    
    async def get_returning_flag(self, session_id: str) -> bool | None:
        """Get returning flag dari Redis"""
        # Using the .get method we just created in RedisClient
        val = await self.redis.get(f"returning:{session_id}")
        if val is None:
            return None
        return bool(int(val))

    async def save_user_data(self, session_id: str, user_data: dict) -> None:
        await self.redis.save_user_data(session_id, user_data)
    
    async def get_user_data(self, session_id: str) -> Optional[dict]:
        return await self.redis.get_user_data(session_id)
    
    async def delete_session(self, session_id: str) -> None:
        await self.redis.delete_user_data(session_id)
    
    async def is_returning_user(self, session_id: str) -> bool:
        user_data = await self.get_user_data(session_id)
        return user_data is not None

session_service = SessionService()
