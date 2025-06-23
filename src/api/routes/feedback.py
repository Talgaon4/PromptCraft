from fastapi import APIRouter, status, Depends, Query
from sqlalchemy import func
from src.models.models import Prompt, PromptInstance
from src.database.database import Database
from src.models.models import Response, Feedback, Prompt
from src.api.schemas.base import APIResponse
from src.api.schemas.feedback import (
    FeedbackCreate, FeedbackOut, PaginatedFeedback,
    PromptStats, OptimizationReadiness
)
from src.api.exceptions import APIException
import os, json

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
    with db.db_manager.get_session() as s:
        resp = s.get(Response, response_id)
        if not resp:
            raise APIException(404, "Response not found")

        fb = Feedback(response_id=response_id, score=payload.score)
        s.add(fb); s.commit(); s.refresh(fb)
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
    with db.db_manager.get_session() as s:
        if not s.get(Prompt, prompt_id):
            raise APIException(404, "Prompt not found")

        q = (
            s.query(Feedback)
            .join(Response, Feedback.response_id == Response.id)
            .join(PromptInstance, Response.prompt_instance_id == PromptInstance.id)
            .filter(PromptInstance.prompt_id == prompt_id)
        )
        total = q.count()
        items = (
            q.offset(offset).limit(limit).all()
        )
        dto_items = [FeedbackOut.model_validate(fb, from_attributes=True) for fb in items]

    payload = PaginatedFeedback(items=dto_items, total=total, offset=offset, limit=limit)
    return APIResponse(data=payload)

# ---------- GET /feedback (global) ----------
@router.get("/feedback", response_model=APIResponse)
def list_feedback(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    with db.db_manager.get_session() as s:
        q = s.query(Feedback)
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        dto_items = [FeedbackOut.model_validate(fb, from_attributes=True) for fb in items]

    return APIResponse(
        data=PaginatedFeedback(items=dto_items, total=total, offset=offset, limit=limit)
    )

# ---------- GET /prompts/{id}/stats ----------
@router.get("/prompts/{prompt_id}/stats", response_model=APIResponse)
def prompt_stats(prompt_id: str, db: Database = Depends(get_db)):
    with db.db_manager.get_session() as s:
        if not s.get(Prompt, prompt_id):
            raise APIException(404, "Prompt not found")

        total, avg = (
                s.query(func.count(Feedback.id), func.avg(Feedback.score))
                .join(Response, Feedback.response_id == Response.id)
                .join(PromptInstance, Response.prompt_instance_id == PromptInstance.id)
                .filter(PromptInstance.prompt_id == prompt_id)
                .first()
            )
    return APIResponse(data=PromptStats(prompt_id=prompt_id, total_feedback=total, avg_score=avg))

# ---------- GET /prompts/{id}/optimization/readiness ----------
@router.get("/prompts/{prompt_id}/optimization/readiness", response_model=APIResponse)
def readiness(prompt_id: str, db: Database = Depends(get_db)):
    MIN_SAMPLES = 5
    with db.db_manager.get_session() as s:
        if not s.get(Prompt, prompt_id):
            raise APIException(404, "Prompt not found")

        cnt = (
            s.query(func.count(Feedback.id))
            .join(Response, Feedback.response_id == Response.id)
            .join(PromptInstance, Response.prompt_instance_id == PromptInstance.id)
            .filter(PromptInstance.prompt_id == prompt_id)
            .scalar()
        )
    ready = cnt >= MIN_SAMPLES
    reason = "enough samples" if ready else f"need at least {MIN_SAMPLES-cnt} more samples"
    return APIResponse(data=OptimizationReadiness(prompt_id=prompt_id, ready=ready, reason=reason))
