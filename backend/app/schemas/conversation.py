from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.analysis import AnalysisResult
from app.schemas.document import DocumentMetadata

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Document Analysis Conversation"
    document_ids: Optional[List[str]] = None

class ConversationSummary(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    document_count: int = 0
    message_count: int = 0

class ConversationDetail(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    documents: List[DocumentMetadata] = []
    messages: List[AnalysisResult] = []

class ConversationMessageRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
