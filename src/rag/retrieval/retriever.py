from typing import List, Any, Optional
from pydantic import PrivateAttr
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSerializable, RunnableConfig
from src.rag.db.docstore import DocStore
from src.rag.db.vectorstore import VectorStore
from src.rag.utils.collection_handler import get_active_collection
from src.services import get_embeddings
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

class ParentChildRetriever(RunnableSerializable):
    _vector_store: Any = PrivateAttr()
    _doc_store: Any = PrivateAttr()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        active_collection = get_active_collection(["collection_name"])
        logger.info(f"Using Active Collection: {active_collection}")
        self._vector_store = VectorStore.get_vector_store(
            embedding_model=get_embeddings(),
            collection_name=active_collection
        )
        self._doc_store = DocStore.get_doc_store(collection_name=active_collection)
    def invoke(self, query: str, config: Optional[RunnableConfig] = None) -> List[Document]:
        # Search Child Chunk
        results = self._vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=settings.vector_search_k,
            score_threshold=settings.score_threshold,
            filter={"type": "child"}
        )
        if not results:
            return []
        # Map to Parent Chunk
        unique_parent_map = {}
        for child_doc, score in results:
            pid = child_doc.metadata.get("parent_id")
            if pid and pid not in unique_parent_map:
                unique_parent_map[pid] = {
                    "score": score,
                    "content": child_doc.page_content
                }
        # Retrieve Parent Chunk
        parent_ids = list(unique_parent_map.keys())
        try:
            parent_docs = self._doc_store.mget(parent_ids)
        except Exception as e:
            print(f"Error fetching parents: {e}")
            return []
        # Order Parent Chunk by Highest Score
        final_results = []
        for pid, p_doc in zip(parent_ids, parent_docs):
            if p_doc:
                ref_data = unique_parent_map[pid]
                p_doc.metadata["retrieval_score"] = ref_data["score"]
                p_doc.metadata["matched_child_content"] = ref_data["content"]
                final_results.append(p_doc)
        final_results.sort(key=lambda x: x.metadata.get("retrieval_score", 0), reverse=True)
        return final_results[:settings.max_results]