import asyncio
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.rag.retrieval.retriever import ParentChildRetriever
from src.services import PromptService
from src.services.llm_service import llm_service
from src.rag.utils.parser import document_parser
from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger(__name__)

class RAGPipeline:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.chroma_retriever = None
        self.llm = llm_service.llm.bind(
                                        temperature=0.2,      
                                        max_tokens=600       
                                        ).with_retry(
                                        stop_after_attempt=settings.llm_max_retries,
                                        wait_exponential_jitter=True
                                        )
        self.output_parser = StrOutputParser()
        self.prompt = PromptService.format_rag_prompt()

    async def initialize(self):
        try:
            self.chroma_retriever = ParentChildRetriever()
            logger.info("RAG Pipeline initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG Pipeline: {e}")
            return False
    
    async def _ensure_initialize(self):
        async with self._lock:
            if self.chroma_retriever is None:
                logger.info("RAG Pipeline not initialized, doing initialization")
                if not await self.initialize(): 
                    raise RuntimeError(
                        "RAG Pipeline not available. Please run /ingest endpoint first to index documents"
                    )

    async def chat(self):
        await self._ensure_initialize()
        chat_pipeline = (
            RunnablePassthrough.assign(docs=itemgetter("question") | self.chroma_retriever)
            | RunnablePassthrough.assign(
                context=lambda x: document_parser(x["docs"]),
                history=lambda _: []
            )
            | self.prompt
            | self.llm
            | self.output_parser
        )
        return chat_pipeline

    async def evaluate(self):
        await self._ensure_initialize()
        eval_pipeline = (
            RunnablePassthrough.assign(docs=itemgetter("question") | self.chroma_retriever)
            | RunnablePassthrough.assign(
                context=lambda x: document_parser(x["docs"]),
            )
            | RunnablePassthrough.assign(answer=self.prompt | self.llm | self.output_parser)
        )
        return eval_pipeline

rag_pipeline = RAGPipeline()