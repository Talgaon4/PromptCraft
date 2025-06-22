from datetime import datetime
from fastapi import APIRouter
from src.api.schemas.base import APIResponse

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    payload = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
    # Wrap in standard envelope
    return APIResponse(data=payload)
