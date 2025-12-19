from typing import Optional
from src.infrastructure.redis import redis_client
from src.core.logging import get_logger

logger = get_logger(__name__)

class SessionService:
    def __init__(self):
        self.redis = redis_client
    
    def save_user_data(self, session_id: str, user_data: dict) -> None:
        self.redis.save_user_data(session_id, user_data)
    
    def get_user_data(self, session_id: str) -> Optional[dict]:
        return self.redis.get_user_data(session_id)
    
    def delete_session(self, session_id: str) -> None:
        self.redis.delete_user_data(session_id)
    
    def is_returning_user(self, session_id: str) -> bool:
        user_data = self.get_user_data(session_id)
        return user_data is not None

session_service = SessionService()
