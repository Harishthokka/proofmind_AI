import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from app.schemas.conversation import (
    ConversationCreate,
    ConversationSummary,
    ConversationDetail,
    ConversationMessageRequest
)
from app.schemas.analysis import AnalysisResult
from app.schemas.document import DocumentMetadata
from app.services.db_service import db_service
from app.services.decision_service import decision_service
from app.services.pdf_service import pdf_service
from app.routers.auth import get_optional_current_user
from app.routers.documents import process_pdf_file, sanitize_filename

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationSummary])
def list_conversations(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """Lists all conversations for the authenticated user."""
    convs = db_service.get_user_conversations(current_user["id"])
    summaries = []
    for c in convs:
        doc_ids = db_service.get_conversation_documents(c["id"])
        msgs = db_service.get_conversation_messages(c["id"])
        summaries.append(
            ConversationSummary(
                id=c["id"],
                user_id=c["user_id"],
                title=c["title"],
                created_at=c["created_at"],
                updated_at=c["updated_at"],
                document_count=len(doc_ids),
                message_count=len(msgs)
            )
        )
    return summaries

@router.post("", response_model=ConversationDetail)
def create_conversation(
    req: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Creates a new private conversation workspace for the user."""
    conv_id = f"conv-{uuid.uuid4().hex[:8]}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = req.title or "New Document Analysis Conversation"

    conv = db_service.create_conversation(conv_id, current_user["id"], title, created_at)

    # Link initial document_ids if provided
    if req.document_ids:
        for doc_id in req.document_ids:
            doc = db_service.get_document_by_id(doc_id)
            if doc and doc["owner_user_id"] == current_user["id"]:
                db_service.link_document_to_conversation(conv_id, doc_id)

    return get_conversation_details(conv_id, current_user)

@router.get("/{conv_id}", response_model=ConversationDetail)
def get_conversation_details(
    conv_id: str,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Returns conversation details, linked document metadata, and message history."""
    conv = db_service.get_conversation_by_id(conv_id, current_user["id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found or access unauthorized.")

    linked_doc_ids = db_service.get_conversation_documents(conv_id)
    doc_metadatas = []
    for doc_id in linked_doc_ids:
        doc = db_service.get_document_by_id(doc_id)
        if doc:
            doc_metadatas.append(
                DocumentMetadata(
                    id=doc["id"],
                    filename=doc["filename"],
                    file_size=doc["file_size"],
                    page_count=doc["page_count"],
                    uploaded_at=doc["uploaded_at"],
                    content_summary=doc.get("summary"),
                    freshness_date=doc.get("freshness_date"),
                    status=doc.get("status", "PROCESSED"),
                    total_chars=doc.get("total_chars", 0)
                )
            )

    msgs_raw = db_service.get_conversation_messages(conv_id)
    msgs = [AnalysisResult(**m) for m in msgs_raw]

    return ConversationDetail(
        id=conv["id"],
        user_id=conv["user_id"],
        title=conv["title"],
        created_at=conv["created_at"],
        updated_at=conv["updated_at"],
        documents=doc_metadatas,
        messages=msgs
    )

@router.post("/{conv_id}/messages", response_model=AnalysisResult)
def send_conversation_message(
    conv_id: str,
    req: ConversationMessageRequest,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """
    Submits a question in the conversation.
    Retrieves evidence from authorized documents linked to this conversation (or user documents),
    analyzes sufficiency, and appends message result to history.
    """
    conv = db_service.get_conversation_by_id(conv_id, current_user["id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found or access unauthorized.")

    # Get authorized documents for this conversation
    linked_doc_ids = db_service.get_conversation_documents(conv_id)
    
    # If explicit document_ids provided in request, use them; otherwise use conversation linked docs; fallback to all user docs
    if req.document_ids:
        target_ids = [d_id for d_id in req.document_ids]
    elif linked_doc_ids:
        target_ids = linked_doc_ids
    else:
        user_docs = db_service.get_user_documents(current_user["id"])
        target_ids = [d["id"] for d in user_docs]

    # Fetch full document records for authorized target IDs
    docs_to_analyze = []
    for d_id in target_ids:
        d = db_service.get_document_by_id(d_id)
        if d and d["owner_user_id"] == current_user["id"]:
            docs_to_analyze.append(d)
            # Ensure document is linked to conversation
            db_service.link_document_to_conversation(conv_id, d_id)

    # Automatically set conversation title from first question if title is default
    if conv["title"] == "New Document Analysis Conversation":
        new_title = req.question[:40] + ("..." if len(req.question) > 40 else "")
        db_service.create_conversation(conv_id, current_user["id"], new_title, conv["created_at"])

    # Run evidence-aware decision analysis
    result = decision_service.analyze_question(req.question, docs_to_analyze)
    result.conversation_id = conv_id

    # Persist message record to database
    db_service.save_message({
        **result.model_dump(),
        "user_id": current_user["id"],
        "conversation_id": conv_id
    })

    return result

@router.post("/{conv_id}/upload-and-reanalyze", response_model=AnalysisResult)
async def upload_additional_document_and_reanalyze(
    conv_id: str,
    file: UploadFile = File(...),
    original_question: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """
    PHASE 6: Uploads an additional document to the conversation and automatically
    re-analyzes the unanswered question against all accumulated authorized documents!
    """
    conv = db_service.get_conversation_by_id(conv_id, current_user["id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found or access unauthorized.")

    # 1. Process and upload the new PDF file for current user
    upload_res = await process_pdf_file(file, current_user_id=current_user["id"])
    doc_id = upload_res.document_id

    # 2. Link newly uploaded document to this conversation
    db_service.link_document_to_conversation(conv_id, doc_id)

    # 3. Determine original question to reanalyze
    target_question = original_question
    if not target_question:
        msgs = db_service.get_conversation_messages(conv_id)
        if msgs:
            target_question = msgs[-1]["question"]
        else:
            target_question = f"Summarize key rules and clauses in {file.filename}"

    # 4. Fetch all accumulated authorized documents for this conversation
    linked_doc_ids = db_service.get_conversation_documents(conv_id)
    docs_to_analyze = []
    for d_id in linked_doc_ids:
        d = db_service.get_document_by_id(d_id)
        if d and d["owner_user_id"] == current_user["id"]:
            docs_to_analyze.append(d)

    # 5. Rerun retrieval & decision classification using updated evidence
    result = decision_service.analyze_question(target_question, docs_to_analyze)
    result.conversation_id = conv_id
    result.summary = f"Re-analyzed after uploading '{file.filename}': {result.summary}"

    # 6. Save updated result message to conversation history
    db_service.save_message({
        **result.model_dump(),
        "user_id": current_user["id"],
        "conversation_id": conv_id
    })

    return result

@router.delete("/{conv_id}")
def delete_conversation(
    conv_id: str,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Deletes a conversation workspace."""
    conv = db_service.get_conversation_by_id(conv_id, current_user["id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    
    with db_service._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?", (conv_id, current_user["id"]))
        conn.commit()

    return {"message": "Conversation deleted successfully."}
