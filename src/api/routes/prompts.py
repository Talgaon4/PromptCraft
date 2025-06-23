from fastapi import APIRouter, status, Depends, Query
from src.api.schemas.prompt import (
    PromptCreate,
    PromptUpdate,
    PromptOut,
    PaginatedPrompts,
)
from src.api.schemas.base import APIResponse
from src.api.exceptions import APIException
from src.database.database import Database
from src.models.models import Prompt
from src.services.prompt_service import PromptService
import os

router = APIRouter(prefix="/prompts", tags=["Prompts"])

# Dependency to obtain DB instance (keeps things testable)
def get_db():
    return Database(os.getenv("DATABASE_URL"))

@router.post("", response_model=APIResponse,
             status_code=status.HTTP_201_CREATED)
def create_prompt(payload: PromptCreate,
                  db: Database = Depends(get_db)):
    svc = PromptService(db)
    try:
        prompt_id = svc.create(payload.text, payload.description or "")
        prompt    = svc.get(prompt_id)          
        dto = PromptOut.model_validate(prompt, from_attributes=True)
        return APIResponse(data=dto)
    except Exception as exc:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create prompt",
            errors=[str(exc)],
        )



# ---------- GET single prompt ---------- #
@router.get(
    "/{prompt_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def get_prompt(prompt_id: str, db: Database = Depends(get_db)):
    svc = PromptService(db)
    prompt = svc.get(prompt_id)
    if not prompt:
        raise APIException(status_code=404, message="Prompt not found")
    return APIResponse(data=PromptOut.model_validate(prompt, from_attributes=True))


# ---------- GET list with pagination ---------- #
@router.get(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def list_prompts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    svc = PromptService(db)
    orm_items, total = svc.list_paginated(offset, limit)
    items = [PromptOut.model_validate(p, from_attributes=True) for p in orm_items]
    payload = PaginatedPrompts(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )
    return APIResponse(data=payload)


# ---------- PUT update prompt ---------- #

@router.put(
    "/{prompt_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def update_prompt(
    prompt_id: str,
    payload: PromptUpdate,
    db: Database = Depends(get_db),
):
    svc = PromptService(db)
    prompt = svc.update(prompt_id,
                            text=payload.text,
                            description=payload.description)
    if not prompt:
        raise APIException(404, "Prompt not found")
    
    dto = PromptOut.model_validate(prompt, from_attributes=True)
    return APIResponse(data=dto)