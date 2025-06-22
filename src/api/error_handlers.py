from fastapi import Request, status
from fastapi.responses import JSONResponse

from .schemas.base import APIResponse
from .schemas.exceptions import APIException


def add_error_handlers(app):
    """
    Call once in main.py to register global exception handlers.
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(_: Request, exc: APIException):
        body = APIResponse(
            success=False,
            data=None,
            message=exc.message,
            errors=exc.errors,
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        body = APIResponse(
            success=False,
            message="Internal server error",
            errors=[str(exc)],
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=body.model_dump(),
        )
