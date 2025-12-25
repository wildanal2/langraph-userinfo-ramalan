from typing import Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
import langwatch
from src.infrastructure.aws import get_bedrock_client
from src.core.logging import get_logger
from src.core.exceptions import LLMServiceError
from src.core.config import settings

logger = get_logger(__name__)

class ExtractedData(BaseModel):
    nama: str | None = Field(None, description="Nama lengkap user")
    kota: str | None = Field(None, description="Kota domisili user")
    tanggal_lahir: str | None = Field(None, description="Tanggal lahir user dalam format DD-MM-YYYY. Ekstrak dan konversi dari format apapun (contoh: '12 Desember 2003' menjadi '12-12-2003', '12.10.2002' menjadi '12-10-2002')")
    bidang_ekraf: str | None = Field(None, description="Bidang ekonomi kreatif yang ditekuni")
    jumlah_komunitas_ekraf_disekitar: str | None = Field(None, description="Informasi keberadaan komunitas ekraf di sekitar user. Bisa berupa: 'Ada', 'Ada, banyak', 'Tidak Ada', atau angka/deskripsi lainnya")
    email: str | None = Field(None, description="Alamat email valid")
    no_telepon: str | None = Field(None, description="Nomor telepon")
    harapan: str | None = Field(None, description="Harapan atau tujuan user")

class IntentClassification(BaseModel):
    intent: str = Field(description="'answering' if user is responding to question, 'asking' if user is asking question")

class LLMService:
    def __init__(self):
        self.llm = get_bedrock_client(max_tokens=1000, temperature=0.5)
        self.structured_llm = get_bedrock_client(max_tokens=500, temperature=0.5).with_structured_output(ExtractedData)
        self.intent_llm = get_bedrock_client(max_tokens=20, temperature=0.0).with_structured_output(IntentClassification)
    
    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def ainvoke(self, prompt: str) -> str:
        try:
            config = None
            if settings.langwatch_enabled:
                config = RunnableConfig(
                    callbacks=[langwatch.get_current_trace().get_langchain_callback()]
                )
            response = await self.llm.ainvoke([HumanMessage(content=prompt)], config=config)
            return response.content if isinstance(response.content, str) else ""
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise LLMServiceError(f"LLM invocation failed: {e}")
    
    async def astream(self, prompt: str):
        try:
            config = None
            if settings.langwatch_enabled:
                config = RunnableConfig(
                    callbacks=[langwatch.get_current_trace().get_langchain_callback()]
                )
            async for chunk in self.llm.astream([HumanMessage(content=prompt)], config=config):
                yield chunk
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            raise LLMServiceError(f"LLM streaming failed: {e}")

    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def extract_data(self, prompt: str) -> ExtractedData:
        try:
            config = None
            if settings.langwatch_enabled:
                config = RunnableConfig(
                    callbacks=[langwatch.get_current_trace().get_langchain_callback()]
                )
            return await self.structured_llm.ainvoke(prompt, config=config)
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise LLMServiceError(f"Data extraction failed: {e}")

    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def classify_intent(self, prompt: str) -> str:
        try:
            config = None
            if settings.langwatch_enabled:
                config = RunnableConfig(
                    callbacks=[langwatch.get_current_trace().get_langchain_callback()]
                )
            result = await self.intent_llm.ainvoke(prompt, config=config)
            return result.intent
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            raise LLMServiceError(f"Intent classification failed: {e}")

llm_service = LLMService()
