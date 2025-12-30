from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from src.core.config import settings
import chromadb

class VectorStore:
    @staticmethod
    def get_vector_store(embedding_model: Embeddings, collection_name: str, persist_directory: str = settings.chroma_presist_dir):
        return Chroma(
            embedding_function=embedding_model,
            persist_directory=persist_directory,
            collection_name=collection_name,
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    @staticmethod
    def get_chroma_client(persist_directory: str = settings.chroma_presist_dir):
        return chromadb.PersistentClient(path=persist_directory)