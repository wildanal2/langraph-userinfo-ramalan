import redis
import json
from src.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def save_user_data(session_id: str, user_data: dict):
    redis_client.setex(f"user:{session_id}", 86400, json.dumps(user_data))

def get_user_data(session_id: str) -> dict | None:
    data = redis_client.get(f"user:{session_id}")
    return json.loads(data) if data else None

def delete_user_data(session_id: str):
    redis_client.delete(f"user:{session_id}")
