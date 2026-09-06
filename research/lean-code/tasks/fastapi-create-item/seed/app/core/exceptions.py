"""Exception hierarchy and the handlers that turn every failure into the response envelope.

Input-driven failures never surface as a raw 500: pydantic rejections arrive as
RequestValidationError and leave as a 422 in the envelope; services raise the typed hierarchy.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response_codes import ResponseCodes as RC

logger = logging.getLogger("inventory")


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500,
                 code: str | None = None, data: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code or RC.ERROR
        self.data = data
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: str | None = None) -> None:
        super().__init__(message, status_code=404, code=code or RC.NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str = "Invalid request", code: str | None = None,
                 data: Any = None) -> None:
        super().__init__(message, status_code=400, code=code or RC.BAD_REQUEST, data=data)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", code: str | None = None) -> None:
        super().__init__(message, status_code=401, code=code or RC.UNAUTHORIZED)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", code: str | None = None) -> None:
        super().__init__(message, status_code=409, code=code or RC.CONFLICT)


class ValidationException(AppException):
    """Semantic validation a service performs AFTER pydantic accepted the shape."""

    def __init__(self, message: str = "Validation error", code: str | None = None,
                 data: Any = None) -> None:
        super().__init__(message, status_code=422, code=code or RC.VALIDATION_ERROR, data=data)


def _error(request: Request, status_code: int, code: str, message: str, **extra: Any) -> JSONResponse:
    body: dict[str, Any] = {"status": "error", "code": code, "message": message,
                            "path": request.url.path, **extra}
    return JSONResponse(status_code=status_code, content=body)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.error("app_exception path=%s status=%s code=%s", request.url.path, exc.status_code, exc.code)
    extra = {"data": exc.data} if exc.data is not None else {}
    return _error(request, exc.status_code, exc.code, exc.message, **extra)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"], "type": err["type"]} for err in exc.errors()]
    logger.warning("validation_error path=%s errors=%d", request.url.path, len(details))
    return _error(request, 422, RC.VALIDATION_ERROR, "Validation error", details=details)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Framework-raised HTTPException (404 unknown path, 405) wrapped in the envelope."""
    code_map = {404: RC.NOT_FOUND, 405: RC.BAD_REQUEST, 401: RC.UNAUTHORIZED,
                403: RC.FORBIDDEN, 409: RC.CONFLICT}
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return _error(request, exc.status_code, code_map.get(exc.status_code, RC.ERROR), message)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception path=%s type=%s", request.url.path, type(exc).__name__)
    return _error(request, 500, RC.INTERNAL_SERVER_ERROR, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
