from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-southeast-3"  # Default region for LLM (Jakarta)
    aws_embedding_region: str = "ap-northeast-1"  # Region for embeddings
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    bedrock_embedding_model_id: str
    # Application Configuration
    app_name: str = "Creative Fortune Teller API"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    
    # Security
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8181"]
    max_request_size: int = 1024 * 1024  # 1MB
    rate_limit_per_minute: int = 60
    
    # External Services
    sso_register_url: str = "https://your-sso-link.com/register"
    redis_url: str = "redis://default@127.0.0.1:6379"
    redis_ttl: int = 86400  # 24 hours
    check_email_url: str = "http://localhost:8000/auth/check-email"
    auth_username: str = "username"
    auth_password: str = "password"
    
    # LLM Configuration
    llm_timeout: int = 30
    llm_max_retries: int = 3
    
    # LangWatch Configuration
    langwatch_api_key: str = ""
    langwatch_endpoint: str = "https://app.langwatch.ai"
    langwatch_enabled: bool = True
    
    # LangWatch Configuration
    langwatch_api_key: str = ""
    langwatch_endpoint: str = "https://app.langwatch.ai"
    langwatch_enabled: bool = True
    
    # RAG
    chroma_presist_dir : str
    active_collection_file : str
    max_results : int
    vector_search_k : int
    score_threshold : float
    
    class Config:
        env_file = ".env"

settings = Settings()
