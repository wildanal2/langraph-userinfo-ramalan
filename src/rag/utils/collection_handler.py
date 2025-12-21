from datetime import datetime
import json
import os
from src.core.config import settings
from src.core.logging import get_logger
from src.rag.db.vectorstore import VectorStore
from src.rag.db.docstore import DocStore

logger = get_logger(__name__)

def get_new_collection() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"rag_v_{timestamp}"

def set_active_collection(collection_name: str, chunking_config: dict):
    config = {
        'collection_name': collection_name,
        'updated_at': datetime.now().isoformat(),
        'chunking_config': chunking_config
    }
    os.makedirs(os.path.dirname(settings.active_collection_file), exist_ok=True)
    with open(settings.active_collection_file, 'w') as f:
        json.dump(config, f, indent=2)
    logger.info(f"Active collection switched to: {collection_name}")
    return config

def get_active_collection(keys, file_path=settings.active_collection_file):
    with open(file_path, "r") as f:
        data = json.load(f)
    if len(keys) == 1:
        return data.get(keys[0])
    return {key: data.get(key) for key in keys}

def delete_old_collections():
    client = VectorStore.get_chroma_client()
    all_collections = client.list_collections()
    rag_collections = [col for col in all_collections if col.name.startswith("rag_v_")]
    rag_collections.sort(key=lambda x: x.name)
    active_collection = get_active_collection(["collection_name"])
    to_delete = [col for col in rag_collections if col.name != active_collection]
    if not to_delete:
        logger.info("No collections to delete")
        return
    for col in to_delete:
        collection_name = col.name
        try:
            client.delete_collection(collection_name)
            logger.info(f"Deleted ChromaDB collection: {collection_name}")
            DocStore.clear_namespace(collection_name)
            logger.info(f"Cleared Redis namespace: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete old collection {collection_name}: {e}")