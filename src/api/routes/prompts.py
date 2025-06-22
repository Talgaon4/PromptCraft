from fastapi import APIRouter, status, Depends, Query
from sqlalchemy import select 
from src.models.models import Prompt
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
import os

router = APIRouter(prefix="/prompts", tags=["Prompts"])

# Dependency to obtain DB instance (keeps things testable)
def get_db():
    return Database(os.getenv("DATABASE_URL"))

@router.post(
    "",                           # /api/v1/prompts
    response_model=APIResponse,   # wrapper with PromptOut in data
    status_code=status.HTTP_201_CREATED,
)
def create_prompt(
    payload: PromptCreate,
    db: Database = Depends(get_db),
):
    """
    Create a new prompt. Wrapper returns APIResponse→data=PromptOut
    """
    try:
        prompt = db.create_prompt(payload.text, payload.description or "")
        return APIResponse(data=PromptOut.model_validate(prompt, from_attributes=True))
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
    prompt = db.get_prompt(prompt_id)
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
    with db.db_manager.get_session() as session:
        orm_items = (
            session.query(Prompt)
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = session.query(Prompt).count()
        items = [
                    PromptOut.model_validate(p, from_attributes=True) for p in orm_items
                ]
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
    with db.db_manager.get_session() as session:
        prompt = session.get(Prompt, prompt_id)
        if not prompt:
            raise APIException(status_code=404, message="Prompt not found")

        if payload.text is not None:
            prompt.text = payload.text
        if payload.description is not None:
            prompt.description = payload.description
        prompt.version += 1

        session.commit()
        session.refresh(prompt)

        # 🔑  Convert while still attached
        dto = PromptOut.model_validate(prompt, from_attributes=True)

    return APIResponse(data=dto)