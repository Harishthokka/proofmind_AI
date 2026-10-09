from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.analysis import AnalysisRequest, AnalysisResult, AnalysisUpdateRequest
from app.routers.documents import uploaded_documents_db
from app.services.decision_service import decision_service
from app.services.db_service import db_service
from app.routers.auth import get_optional_current_user

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"])

# In-memory history store for backward compatibility
analysis_history_db: List[AnalysisResult] = []

@router.post("/run", response_model=AnalysisResult)
def run_analysis(
    request: AnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """
    Runs evidence-aware AI analysis for a given question against uploaded documents.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question prompt cannot be empty.")

    # Get user documents from SQLite database
    user_docs = db_service.get_user_documents(current_user["id"])

    # Filter documents if specific document_ids provided
    docs_to_analyze = user_docs
    if request.document_ids:
        docs_to_analyze = [d for d in user_docs if d["id"] in request.document_ids]

    result = decision_service.analyze_question(request.question, docs_to_analyze)
    
    # Save message to database if conversation_id or user session exists
    if current_user["id"]:
        db_service.save_message({
            **result.model_dump(),
            "user_id": current_user["id"],
            "conversation_id": f"conv-{current_user['id'][:8]}"
        })

    analysis_history_db.insert(0, result)  # Prepend newest analysis for in-memory legacy calls
    return result

@router.get("/history", response_model=List[AnalysisResult])
def get_analysis_history(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """Returns analysis history for the authenticated user."""
    user_msgs = db_service.get_user_messages(current_user["id"])
    if user_msgs:
        return [AnalysisResult(**m) for m in user_msgs]
    return []

@router.get("/{analysis_id}", response_model=AnalysisResult)
def get_analysis_by_id(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Returns details for a specific analysis run owned by current user."""
    msg = db_service.get_message_by_id(analysis_id)
    if msg and msg.get("user_id") == current_user["id"]:
        return AnalysisResult(**msg)
        
    for item in analysis_history_db:
        if item.id == analysis_id:
            return item
            
    raise HTTPException(status_code=404, detail="Analysis record not found.")

@router.patch("/{analysis_id}", response_model=AnalysisResult)
def update_analysis(
    analysis_id: str,
    update_data: AnalysisUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Updates an existing analysis result (grounded answer, summary, decision_status, question, analyst_notes)."""
    msg = db_service.get_message_by_id(analysis_id)
    if not msg:
        # Check in-memory legacy list
        for item in analysis_history_db:
            if item.id == analysis_id:
                if update_data.grounded_answer is not None:
                    item.grounded_answer = update_data.grounded_answer
                if update_data.summary is not None:
                    item.summary = update_data.summary
                if update_data.question is not None:
                    item.question = update_data.question
                if update_data.decision_status is not None:
                    item.decision_status = update_data.decision_status
                if update_data.analyst_notes is not None:
                    item.analyst_notes = update_data.analyst_notes
                item.is_edited = True
                return item
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    if msg.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to target analysis.")

    updated = db_service.update_message(analysis_id, current_user["id"], update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update analysis.")

    res = AnalysisResult(**updated)
    res.is_edited = True
    if update_data.analyst_notes:
        res.analyst_notes = update_data.analyst_notes
    return res

