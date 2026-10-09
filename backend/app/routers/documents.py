import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from app.schemas.document import DocumentMetadata, DocumentUploadResponse, DocumentUpdateRequest
from app.services.pdf_service import pdf_service
from app.services.db_service import db_service
from app.routers.auth import get_optional_current_user

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

# In-memory index of uploaded documents associated with saved disk files for fast legacy lookup
uploaded_documents_db: List[dict] = []

# Storage directory for uploaded PDF files
UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOADS_DIR, exist_ok=True)

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

def sanitize_filename(filename: str) -> str:
    """Sanitizes user filename to prevent path traversal or unsafe characters."""
    clean_name = os.path.basename(filename)
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)

@router.get("", response_model=List[DocumentMetadata])
def get_documents(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """Returns list of uploaded documents belonging to the authenticated user."""
    user_docs = db_service.get_user_documents(current_user["id"])
    return [
        DocumentMetadata(
            id=d["id"],
            filename=d["filename"],
            file_size=d["file_size"],
            page_count=d["page_count"],
            uploaded_at=d["uploaded_at"],
            content_summary=d.get("summary"),
            freshness_date=d.get("freshness_date", datetime.now().strftime("%Y-%m-%d")),
            status=d.get("status", "PROCESSED"),
            total_chars=d.get("total_chars", 0)
        )
        for d in user_docs
    ]

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_single_document(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Uploads, validates, and processes a single PDF document for the authenticated user."""
    return await process_pdf_file(file, current_user_id=current_user["id"])

@router.post("/upload-batch", response_model=List[DocumentUploadResponse])
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Uploads and processes multiple PDF documents in batch."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided in upload request.")
    
    results = []
    for file in files:
        res = await process_pdf_file(file, current_user_id=current_user["id"])
        results.append(res)
    return results

async def process_pdf_file(file: UploadFile, current_user_id: str = "demo-user-id") -> DocumentUploadResponse:
    # 1. Extension Validation
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format for '{file.filename}'. ProofMind AI requires valid PDF documents."
        )

    # 2. Read File Contents & Check Empty / Size Limit
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file '{file.filename}' is empty (0 bytes)."
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' exceeds the maximum allowed size of 25MB."
        )

    # 3. PDF Parsing & Text Extraction
    try:
        extracted = pdf_service.extract_text_and_metadata(contents, file.filename)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as parse_err:
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed for '{file.filename}'. The file structure may be corrupted."
        )

    # 4. Generate Unique ID & Save File to Server Uploads Directory
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    clean_name = sanitize_filename(file.filename)
    safe_filepath = os.path.join(UPLOADS_DIR, f"{doc_id}_{clean_name}")

    try:
        with open(safe_filepath, "wb") as f:
            f.write(contents)
    except Exception as save_err:
        raise HTTPException(status_code=500, detail="Failed to persist uploaded document file to storage.")

    # 5. Store Metadata Record to Database & In-Memory Index
    uploaded_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_record = {
        "id": doc_id,
        "owner_user_id": current_user_id,
        "filename": file.filename,
        "file_size": file_size,
        "page_count": extracted["page_count"],
        "pages": extracted["pages"],
        "summary": extracted["summary"],
        "total_chars": extracted["total_chars"],
        "uploaded_at": uploaded_at_str,
        "freshness_date": datetime.now().strftime("%Y-%m-%d"),
        "status": extracted["status"],
        "storage_filename": f"{doc_id}_{clean_name}"
    }

    db_service.save_document(doc_record)
    uploaded_documents_db.append(doc_record)

    # Build user message based on status
    if extracted["status"] == "NO_TEXT_EXTRACTED":
        msg = f"PDF uploaded, but no extractable text was found (scanned image PDF without OCR)."
    else:
        msg = f"PDF '{file.filename}' processed successfully: {extracted['page_count']} page(s) and {extracted['total_chars']} characters extracted."

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        page_count=extracted["page_count"],
        file_size=file_size,
        status=extracted["status"],
        message=msg,
        total_chars=extracted["total_chars"],
        uploaded_at=uploaded_at_str
    )

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Deletes an uploaded document and removes its file from storage if owned by authenticated user."""
    global uploaded_documents_db
    target_doc = db_service.get_document_by_id(document_id)
    
    if not target_doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if target_doc["owner_user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to target document.")

    # Remove stored file if exists
    storage_name = target_doc.get("storage_filename")
    if storage_name:
        filepath = os.path.join(UPLOADS_DIR, storage_name)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

    db_service.delete_document(document_id, target_doc["owner_user_id"])
    uploaded_documents_db = [d for d in uploaded_documents_db if d["id"] != document_id]
    
    return {"message": f"Document '{target_doc['filename']}' removed successfully."}

@router.patch("/{document_id}", response_model=DocumentMetadata)
def update_document(
    document_id: str,
    update_data: DocumentUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Updates document metadata (filename, content_summary, freshness_date)."""
    target_doc = db_service.get_document_by_id(document_id)
    if not target_doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if target_doc["owner_user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to target document.")

    updated = db_service.update_document(document_id, current_user["id"], update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update document.")

    return DocumentMetadata(
        id=updated["id"],
        filename=updated["filename"],
        file_size=updated["file_size"],
        page_count=updated["page_count"],
        uploaded_at=updated["uploaded_at"],
        content_summary=updated.get("summary"),
        freshness_date=updated.get("freshness_date", datetime.now().strftime("%Y-%m-%d")),
        status=updated.get("status", "PROCESSED"),
        total_chars=updated.get("total_chars", 0),
        is_edited=True
    )

