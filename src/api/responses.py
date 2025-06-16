from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = []
    timestamp: str = datetime.utcnow().isoformat()

class PromptResult(APIResponse):
    @classmethod
    def success(cls, prompt_data: dict, message: str = "Success"):
        return cls(success=True, data=prompt_data, message=message)
    
    @classmethod
    def error(cls, errors: List[str], message: str = "Error occurred"):
        return cls(success=False, errors=errors, message=message)

class OperationResult(APIResponse):
    @classmethod
    def success(cls, data: Any = None, message: str = "Operation completed"):
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error(cls, errors: List[str], message: str = "Operation failed"):
        return cls(success=False, errors=errors, message=message)