import uuid
from typing import List, Dict
from src.rag.db.docstore import DocStore
from src.rag.db.vectorstore import VectorStore
from src.services import get_embeddings
from langchain_core.documents import Document
from src.core.logging import get_logger

logger = get_logger(__name__)
class ParentChildIndexer:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.embedding_model = get_embeddings()
        self.vector_store = VectorStore.get_vector_store(
            embedding_model=self.embedding_model,
            collection_name=collection_name
        )
        self.doc_store = DocStore.get_doc_store(collection_name=collection_name)
        logger.info(f"Initialized ParentChildIndexer for collection: {collection_name}")

    def index_documents(self, split_result: Dict[str, List[Document]]) -> None:
        parent_docs = split_result.get("parents", [])
        child_docs = split_result.get("children", [])
        logger.info(f"Indexing {len(parent_docs)} Parents & {len(child_docs)} Children")
        # Simpan Parent Chunk ke Redis
        if parent_docs:
            try:
                parent_key_value_pairs = []
                for doc in parent_docs:
                    doc_id = doc.metadata.get("doc_id") or str(uuid.uuid4())
                    doc.metadata["doc_id"] = doc_id
                    parent_key_value_pairs.append((doc_id, doc))
                self.doc_store.mset(parent_key_value_pairs)
                logger.info(f"Saved {len(parent_docs)} Parent Chunks to Redis")
            except Exception as e:
                logger.error(f"Error saving Parent Chunks to Redis: {e}")
                raise e
        # Simpan Child Chunk ke ChromaDB
        if child_docs:
            try:
                valid_children = [d for d in child_docs if "parent_id" in d.metadata]
                self.vector_store.add_documents(valid_children)
                logger.info(f"Saved {len(valid_children)} Child Chunks to ChromaDB.")
            except Exception as e:
                logger.error(f"Error saving Child Chunks to Chroma: {e}")
                raise e
        return None