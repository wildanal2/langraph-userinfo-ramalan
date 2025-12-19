from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    sso_register_url: str = "https://your-sso-link.com/register"
    redis_url: str = "redis://default@127.0.0.1:6379"
    
    class Config:
        env_file = ".env"

settings = Settings()
