from fastapi import APIRouter, status, Depends, Query
from src.database.database import Database
from src.models.models import Prompt, PromptInstance, Response
from src.api.exceptions import APIException
from src.api.schemas.base import APIResponse
from src.api.schemas.instance import (
    PromptInstanceCreate,
    ResponseCreate,
    PromptInstanceOut,
    ResponseOut,
    PaginatedInstances,
    PaginatedResponses,
)
import os
import json

router = APIRouter(prefix="/instances", tags=["Prompt Instances / Responses"])
router = APIRouter(tags=["Prompt Instances / Responses"])

# ----------------- helpers -----------------
def get_db():
    return Database(os.getenv("DATABASE_URL"))


# ------------ POST /prompts/{id}/instances -------------
@router.post(
    "/prompts/{prompt_id}/instances",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_instance(
    prompt_id: str,
    payload: PromptInstanceCreate,
    db: Database = Depends(get_db),
):
    with db.db_manager.get_session() as session:
        # make sure prompt exists
        if not session.get(Prompt, prompt_id):
            raise APIException(404, "Prompt not found")

        inst = PromptInstance(
            prompt_id=prompt_id,
            formatted_text=payload.formatted_text,
            context=payload.context and str(payload.context),  # store as JSON string
        )
        session.add(inst)
        session.commit()
        session.refresh(inst)

        dto = PromptInstanceOut.model_validate(inst, from_attributes=True)
    return APIResponse(data=dto)


# ------------- POST /instances/{id}/responses -----------
@router.post(
    "/instances/{instance_id}/responses",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_response(
    instance_id: str,
    payload: ResponseCreate,
    db: Database = Depends(get_db),
):
    with db.db_manager.get_session() as session:
        if not session.get(PromptInstance, instance_id):
            raise APIException(404, "Instance not found")

        resp = Response(
            prompt_instance_id=instance_id,
            content=payload.content,
            response_metadata=json.dumps(payload.metadata or {}),
        )
        session.add(resp)
        session.commit()
        session.refresh(resp)

        dto = ResponseOut(
            id=resp.id,
            prompt_instance_id=resp.prompt_instance_id,
            content=resp.content,
            metadata=payload.metadata or {},
            created_at=resp.created_at,
        )
    return APIResponse(data=dto)


# --------- GET /prompts/{id}/instances (history) -------
@router.get(
    "/prompts/{prompt_id}/instances",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def list_instances(
    prompt_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    with db.db_manager.get_session() as session:
        q = (
            session.query(PromptInstance)
            .filter(PromptInstance.prompt_id == prompt_id)
        )
        total = q.count()
        orm_items = q.offset(offset).limit(limit).all()
        items = [PromptInstanceOut.model_validate(i, from_attributes=True) for i in orm_items]

    payload = PaginatedInstances(items=items, total=total, offset=offset, limit=limit)
    return APIResponse(data=payload)


# -------- GET /instances/{id}/responses (list) ---------
@router.get(
    "/instances/{instance_id}/responses",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def list_responses(
    instance_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_db),
):
    with db.db_manager.get_session() as session:
        q = session.query(Response).filter(Response.prompt_instance_id == instance_id)
        total = q.count()
        orm_items = q.offset(offset).limit(limit).all()
        items = [
            ResponseOut(
                id=r.id,
                prompt_instance_id=r.prompt_instance_id,
                content=r.content,
                metadata=json.loads(r.response_metadata) if r.response_metadata else {},
                created_at=r.created_at,
            )
            for r in orm_items
        ]
    payload = PaginatedResponses(items=items, total=total, offset=offset, limit=limit)
    return APIResponse(data=payload)
