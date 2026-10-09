from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ProofMind AI API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
