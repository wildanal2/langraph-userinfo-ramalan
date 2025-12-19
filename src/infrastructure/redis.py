import redis
import json
from typing import Optional
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import ExternalServiceError

logger = get_logger(__name__)

class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = redis.from_url(
                    settings.redis_url, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                cls._instance.client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                raise ExternalServiceError(f"Redis connection failed: {e}")
        return cls._instance
    
    def save_user_data(self, session_id: str, user_data: dict) -> None:
        try:
            self.client.setex(
                f"user:{session_id}", 
                settings.redis_ttl, 
                json.dumps(user_data)
            )
            logger.debug(f"Saved user data for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save user data: {e}")
            raise ExternalServiceError(f"Failed to save user data: {e}")
    
    def get_user_data(self, session_id: str) -> Optional[dict]:
        try:
            data = self.client.get(f"user:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get user data: {e}")
            return None
    
    def delete_user_data(self, session_id: str) -> None:
        try:
            self.client.delete(f"user:{session_id}")
            logger.debug(f"Deleted user data for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            raise ExternalServiceError(f"Failed to delete user data: {e}")
    
    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False

redis_client = RedisClient()
