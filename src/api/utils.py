# src/api/utils.py  (new file or wherever you keep helpers)
from typing import Any, Optional
from fastapi.responses import JSONResponse

def operation_success(data: Any = None,
                      message: str = "success",
                      status_code: int = 200):
    """
    Standard success envelope.
    Returns a JSONResponse with 2xx status – *never* an exception.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )
