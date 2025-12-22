from functools import lru_cache
from langchain_core.embeddings import Embeddings
from langchain_aws import BedrockEmbeddings
from src.core.config import settings

@lru_cache(maxsize=1)
def get_embeddings(model_id: str = settings.bedrock_embedding_model_id) -> Embeddings:
    return BedrockEmbeddings(
        model_id=model_id, 
        region_name=settings.aws_embedding_region
    )