from pydantic import BaseModel, Field
from typing import Optional

class PromptCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Prompt template text")
    description: Optional[str] = Field(None, description="Optional prompt description")

class InstanceCreate(BaseModel):
    formatted_text: str = Field(..., min_length=1, description="Formatted prompt text")
    context: Optional[str] = Field(None, description="Optional context as JSON string")

class ResponseCreate(BaseModel):
    content: str = Field(..., min_length=1, description="AI response content")
    metadata: Optional[str] = Field(None, description="Optional response metadata")

class FeedbackCreate(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Feedback score between 0.0 and 1.0")