from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PageContent(BaseModel):
    page_number: int
    text: str
    char_count: int

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: int
    uploaded_at: str
    content_summary: Optional[str] = None
    freshness_date: Optional[str] = None
    status: str = "PROCESSED"  # PROCESSED, NO_TEXT_EXTRACTED, EXTRACTION_FAILED
    total_chars: Optional[int] = 0
    is_edited: Optional[bool] = False

class DocumentUpdateRequest(BaseModel):
    filename: Optional[str] = None
    content_summary: Optional[str] = None
    freshness_date: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    file_size: int
    status: str
    message: str
    total_chars: int
    uploaded_at: str
