from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = []
    timestamp: str = datetime.utcnow().isoformat()

class PromptResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = []
    timestamp: str = datetime.utcnow().isoformat()
    
    @classmethod
    def success_response(cls, prompt_data: dict, message: str = "Success"):
        return cls(
            success=True, 
            data=prompt_data, 
            message=message,
            errors=[],
            timestamp=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def error_response(cls, errors: List[str], message: str = "Error occurred"):
        return cls(
            success=False, 
            data=None,
            message=message,
            errors=errors,
            timestamp=datetime.utcnow().isoformat()
        )

class OperationResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = []
    timestamp: str = datetime.utcnow().isoformat()
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Operation completed"):
        return cls(
            success=True, 
            data=data, 
            message=message,
            errors=[],
            timestamp=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def error_response(cls, errors: List[str], message: str = "Operation failed"):
        return cls(
            success=False, 
            data=None,
            message=message,
            errors=errors,
            timestamp=datetime.utcnow().isoformat()
        )