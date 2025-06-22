from pydantic import BaseModel, Field
from datetime import datetime 

# ---------- Client → Server ----------
class PromptCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    description: str | None = Field(default=None, max_length=500)


# ---------- Server → Client ----------
class PromptOut(BaseModel):
    id: str
    text: str
    version: int
    description: str | None
    created_at: datetime
    updated_at: datetime

class PromptUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=10_000)
    description: str | None = Field(default=None, max_length=500)

class PaginatedPrompts(BaseModel):
    items: list[PromptOut]
    total: int
    offset: int
    limit: int