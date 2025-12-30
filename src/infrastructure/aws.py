from langchain_aws import ChatBedrock
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_bedrock_client = None

def get_bedrock_client(max_tokens : int, temperature : int) -> ChatBedrock:
    global _bedrock_client
    if _bedrock_client is None:
        try:
            _bedrock_client = ChatBedrock(
                model_id=settings.bedrock_model_id,
                region_name=settings.aws_region,
                credentials_profile_name=None,
                max_tokens=max_tokens,
                temperature=temperature
            )
            logger.info(f"Bedrock client initialized: {settings.bedrock_model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    return _bedrock_client
