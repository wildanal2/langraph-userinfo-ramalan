import time
import tempfile
from src.rag.utils.collection_handler import get_new_collection, set_active_collection, delete_old_collections
from src.rag.db.docstore import DocStore
from src.rag.db.vectorstore import VectorStore
from src.rag.ingestion.loader import PDFDirectoryLoader, S3FileDownloader
from src.rag.ingestion.splitter import ParentChildSplitter
from src.rag.ingestion.indexer import ParentChildIndexer
from src.rag.retrieval.rag_pipeline import rag_pipeline
from src.core.logging import get_logger

logger = get_logger(__name__)

def ingestion_pipeline(s3_bucket: str, s3_prefix: str, PARENT_CHUNK_SIZE: int, PARENT_CHUNK_OVERLAP: int, CHILD_CHUNK_SIZE: int, CHILD_CHUNK_OVERLAP: int):
    with tempfile.TemporaryDirectory() as tmp_path:
        logger.info(f"Created temporary directory: {tmp_path}")
        new_collection_name = get_new_collection()
        chunking_config = {
            "parent_chunk_size": PARENT_CHUNK_SIZE,
            "parent_chunk_overlap": PARENT_CHUNK_OVERLAP,
            "child_chunk_size": CHILD_CHUNK_SIZE,
            "child_chunk_overlap": CHILD_CHUNK_OVERLAP
        }
        try:
            logger.info("Downloading files from S3 Bucket...")
            s3_downloader = S3FileDownloader()
            success = s3_downloader.download_directory(s3_bucket, s3_prefix, tmp_path)
            if not success:
                return {"status": "error", "message": "No files to process"}
            logger.info("Loading Data...")
            loader = PDFDirectoryLoader() 
            raw_docs = loader.load(tmp_path) 
            logger.info("Splitting Documents...")
            splitter = ParentChildSplitter(
                parent_chunk_size=PARENT_CHUNK_SIZE,
                parent_chunk_overlap=PARENT_CHUNK_OVERLAP,
                child_chunk_size=CHILD_CHUNK_SIZE,
                child_chunk_overlap=CHILD_CHUNK_OVERLAP
            )
            split_result = splitter.split_documents(raw_docs)
            logger.info("Indexing Document Chunks...")
            vector_indexer = ParentChildIndexer(collection_name=new_collection_name)
            result = vector_indexer.index_documents(split_result)
            logger.info("Setting active collection...")
            set_active_collection(new_collection_name, chunking_config)
            logger.info("Initializing RAG Pipeline...")
            rag_pipeline.initialize()
            logger.info("Waiting for remaining queries...")
            time.sleep(3)
            logger.info("Deleting old collections...")
            delete_old_collections()
            logger.info("Ingestion DONE")
            return result
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            logger.info(f"Rollback to old collection...")
            try:
                client = VectorStore.get_chroma_client()
                client.delete_collection(new_collection_name)
                DocStore.clear_namespace(new_collection_name)
                logger.info(f"Rollback DONE")
            except Exception as e:
                logger.error(f"Failed to rollback: {e}")