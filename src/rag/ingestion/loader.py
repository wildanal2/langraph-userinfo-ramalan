import os
import glob
import boto3
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from src.core.logging import get_logger

logger = get_logger(__name__)

class PDFFileLoader:
    def load(self, source: str) -> List[Document]:
        try:
            loader = PyMuPDFLoader(file_path=source)
            documents = loader.load()
            for doc in documents:
                doc.metadata["source_type"] = "pdf"
                doc.metadata["file_path"] = source
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF file: {e}")
            return []

class PDFDirectoryLoader:
    def __init__(self):
        self.single_loader = PDFFileLoader()
    def load(self, source: str, recursive: bool = True) -> List[Document]:
        documents: List[Document] = []
        search_pattern = os.path.join(source, "*.pdf")
        pdf_files = glob.glob(search_pattern)
        if not pdf_files:
            return []
        for file_path in pdf_files:
            if "/." in file_path or "\\." in file_path:
                continue
            docs = self.single_loader.load(file_path)
            documents.extend(docs)
        return documents

class S3FileDownloader:
    def __init__(self):
        self.s3_client = boto3.client('s3')
    def download_directory(self, bucket: str, prefix: str, local_path: str):
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            logger.error("No files found in S3 bucket")
            return False
        for obj in response['Contents']:
            key = obj['Key']
            if key.lower().endswith('.pdf'):
                filename = os.path.basename(key)
                if not filename: 
                    continue 
                local_file_path = os.path.join(local_path, filename)
                logger.info(f"Downloading: {key}")
                self.s3_client.download_file(bucket, key, local_file_path)
        return True