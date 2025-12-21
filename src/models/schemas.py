from pydantic import BaseModel, Field, validator
from typing import Optional

class StartRequest(BaseModel):
    session_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None
    session_state: Optional[dict] = None
    
    @validator('message')
    def sanitize_message(cls, v):
        return v.strip()

class IngestRequest(BaseModel):
    s3_bucket: str
    s3_prefix: str
    parent_chunk_size: int = 1000
    parent_chunk_overlap: int = 100
    child_chunk_size: int = 350
    child_chunk_overlap: int = 50

class ChatResponse(BaseModel):
    content: str
    done: bool
    session_id: Optional[str] = None
    user_data: Optional[dict] = None
    interactive_options: Optional[dict] = None
    fortune_full: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict

class IngestStatusResponse(BaseModel):
    status: str
    message: str
    config: dict