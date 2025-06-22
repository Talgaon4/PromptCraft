from datetime import datetime
from pydantic import BaseModel, Field

# ----------   POST   ----------
class FeedbackCreate(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)

# ----------   DTO   ----------
class FeedbackOut(BaseModel):
    id: str
    response_id: str
    score: float
    created_at: datetime

# ----------   Pagination   ----------
class PaginatedFeedback(BaseModel):
    items: list[FeedbackOut]
    total: int
    offset: int
    limit: int

# ----------   Stats / Readiness ----------
class PromptStats(BaseModel):
    prompt_id: str
    total_feedback: int
    avg_score: float | None = None

class OptimizationReadiness(BaseModel):
    prompt_id: str
    ready: bool
    reason: str
