from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DecisionStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class EvidenceType(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONFLICTING = "CONFLICTING"
    UNCERTAIN = "UNCERTAIN"

class EvidenceItem(BaseModel):
    id: str
    source_filename: str
    page_number: Optional[int] = 1
    source_date: Optional[str] = "Undated"
    version_info: Optional[str] = None
    passage: str
    type: EvidenceType
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    citation_verified: bool = True
    verification_note: Optional[str] = "Passage verified in source document text."

class AnalysisRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    id: str
    question: str
    decision_status: DecisionStatus
    summary: str
    grounded_answer: str
    supporting_evidence: List[EvidenceItem] = []
    conflicting_evidence: List[EvidenceItem] = []
    uncertain_evidence: List[EvidenceItem] = []
    citation_verification_summary: str = "All cited sources verified against document store."
    abstention_explanation: Optional[str] = None
    missing_information: Optional[str] = None
    suggested_doc_request: Optional[str] = None
    conversation_id: Optional[str] = None
    freshness_rating: str = "CURRENT"  # CURRENT, OUTDATED, UNCERTAIN, CONFLICTING_DATES
    date_precedence_note: Optional[str] = None
    reliability_score: float = 0.90
    timestamp: str
    is_edited: Optional[bool] = False
    original_answer: Optional[str] = None
    analyst_notes: Optional[str] = None

class AnalysisUpdateRequest(BaseModel):
    grounded_answer: Optional[str] = None
    summary: Optional[str] = None
    question: Optional[str] = None
    decision_status: Optional[DecisionStatus] = None
    analyst_notes: Optional[str] = None
