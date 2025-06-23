from datetime import datetime
from pydantic import BaseModel, Field


# ----------   POST /prompts/{id}/instances   ----------
class PromptInstanceCreate(BaseModel):
    formatted_text: str = Field(..., min_length=1, max_length=50_000)
    context: dict | None = None            # any extra metadata


# ----------   POST /instances/{id}/responses ----------
class ResponseCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=100_000)
    metadata: dict | None = None


# ----------   DTOs sent back to clients   -------------
class PromptInstanceOut(BaseModel):
    id: str
    prompt_id: str
    formatted_text: str
    context: dict | None
    created_at: datetime


class ResponseOut(BaseModel):
    id: str
    prompt_instance_id: str
    content: str
    metadata: dict | None = Field(None, alias="response_metadata")
    created_at: datetime


# ----------   Pagination wrappers   ------------------
class PaginatedInstances(BaseModel):
    items: list[PromptInstanceOut]
    total: int
    offset: int
    limit: int


class PaginatedResponses(BaseModel):
    items: list[ResponseOut]
    total: int
    offset: int
    limit: int
