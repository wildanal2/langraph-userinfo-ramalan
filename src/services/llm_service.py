from typing import Any
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from src.infrastructure.aws import get_bedrock_client
from src.core.logging import get_logger
from src.core.exceptions import LLMServiceError
from src.core.config import settings

logger = get_logger(__name__)

class ExtractedData(BaseModel):
    nama: str | None = Field(None, description="Nama lengkap user")
    kota: str | None = Field(None, description="Kota domisili user")
    tanggal_lahir: str | None = Field(None, description="Tanggal lahir user")
    bidang_ekraf: str | None = Field(None, description="Bidang ekonomi kreatif yang ditekuni")
    jumlah_komunitas_ekraf_disekitar: str | None = Field(None, description="Jumlah angka komunitas")
    email: str | None = Field(None, description="Alamat email valid")
    no_telepon: str | None = Field(None, description="Nomor telepon")
    harapan: str | None = Field(None, description="Harapan atau tujuan user")

class IntentClassification(BaseModel):
    intent: str = Field(description="'answering' if user is responding to question, 'asking' if user is asking question")

class LLMService:
    def __init__(self):
        self.llm = get_bedrock_client()
        self.structured_llm = self.llm.with_structured_output(ExtractedData)
        self.intent_llm = self.llm.with_structured_output(IntentClassification)
    
    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def invoke(self, prompt: str) -> str:
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content if isinstance(response.content, str) else ""
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise LLMServiceError(f"LLM invocation failed: {e}")
    
    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def extract_data(self, prompt: str) -> ExtractedData:
        try:
            return self.structured_llm.invoke(prompt)
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise LLMServiceError(f"Data extraction failed: {e}")
    
    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def classify_intent(self, prompt: str) -> str:
        try:
            result = self.intent_llm.invoke(prompt)
            return result.intent
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            raise LLMServiceError(f"Intent classification failed: {e}")
    
    def stream(self, prompt: str):
        try:
            return self.llm.stream([HumanMessage(content=prompt)])
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            raise LLMServiceError(f"LLM streaming failed: {e}")

llm_service = LLMService()
