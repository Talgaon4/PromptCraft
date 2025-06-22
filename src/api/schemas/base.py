from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """
    Standard envelope returned by every endpoint.
    """
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
