from langchain_community.storage import RedisStore
from langchain.storage import EncoderBackedStore
from src.core.config import settings
from src.rag.utils.document_serializer import encode, decode, encode_key
from src.core.logging import get_logger
import redis

logger = get_logger(__name__)

class DocStore:
    @staticmethod
    def get_doc_store(collection_name: str, redis_url: str = settings.redis_url):
        namespace = f"{collection_name}"
        try:
            logger.info(f"Connecting to Redis {redis_url}, Namespace: {namespace}")
            raw_store = RedisStore(redis_url=redis_url, namespace=namespace)
            return EncoderBackedStore(
                store=raw_store,
                key_encoder=encode_key,
                value_serializer=encode,
                value_deserializer=decode
            )
        except Exception as e:
            logger.error(f"Gagal koneksi ke Redis: {e}")
            raise e
    
    @staticmethod
    def clear_namespace(collection_name: str, redis_url: str = settings.redis_url):
        try:
            with redis.from_url(redis_url, decode_responses=True) as r:
                keys = list(r.scan_iter(match=f"{collection_name}*"))
                if keys:
                    r.delete(*keys)
                    logger.info(f"Successfully cleared {len(keys)} keys for: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear Redis namespace {collection_name}: {e}")