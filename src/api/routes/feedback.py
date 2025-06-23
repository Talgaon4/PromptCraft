from fastapi import APIRouter, status, Depends, Query
from src.services.feedback_service import FeedbackService
from src.database.database import Database
from src.api.schemas.base import APIResponse
from src.api.schemas.feedback import (
    FeedbackCreate, FeedbackOut, PaginatedFeedback,
    PromptStats, OptimizationReadiness
)
from src.api.exceptions import APIException
from src.services.prompt_service import PromptService
import os

router = APIRouter(tags=["Feedback / Stats"])

def get_db():
    return Database(os.getenv("DATABASE_URL"))

# ---------- POST /responses/{id}/feedback ----------
@router.post(
    "/responses/{response_id}/feedback",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_feedback(
    response_id: str,
    payload: FeedbackCreate,
    db: Database = Depends(get_db),
):
    svc = FeedbackService(db)
    fb  = svc.add_feedback(response_id, payload.score)
    dto = FeedbackOut.model_validate(fb, from_attributes=True)
    return APIResponse(data=dto)

# ---------- GET /prompts/{id}/feedback ----------
@router.get(
    "/prompts/{prompt_id}/feedback",
    response_model=APIResponse,
)
def prompt_feedback(
    prompt_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    svc = FeedbackService(db)
    orm_items, total = svc.list_by_prompt(prompt_id, offset, limit)
    dto_items = [FeedbackOut.model_validate(fb, from_attributes=True) for fb in orm_items]
    payload   = PaginatedFeedback(items=dto_items, total=total, offset=offset, limit=limit)
    return APIResponse(data=payload)

# ---------- GET /feedback (global) ----------
@router.get("/feedback", response_model=APIResponse)
def list_feedback(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    svc = FeedbackService(db)
    dto_items, total = svc.list_all(offset, limit)

    return APIResponse(
        data=PaginatedFeedback(items=dto_items, total=total, offset=offset, limit=limit)
    )

# ---------- GET /prompts/{id}/stats ----------
@router.get("/prompts/{prompt_id}/stats", response_model=APIResponse)
def prompt_stats(prompt_id: str, db: Database = Depends(get_db)):
    svc = FeedbackService(db)
    stats = svc.stats(prompt_id)
    return APIResponse(data=PromptStats(**stats))

# ---------- GET /prompts/{id}/optimization/readiness ----------
@router.get("/prompts/{prompt_id}/optimization/readiness", response_model=APIResponse)
def readiness(prompt_id: str, db: Database = Depends(get_db)):
    psvc = PromptService(db)
    readiness_dict = psvc.ready_for_optimization(prompt_id)
    readiness_dict["prompt_id"] = prompt_id
    return APIResponse(data=OptimizationReadiness(**readiness_dict))