# Reference — FastAPI envelope + exception-handler stack (drop-in)

Production-extracted implementation of the envelope convention in the skill. One error shape, one
success shape, five handlers — input-driven failures never surface as a raw 500.

Envelope:

```
success: {"status": "success", "code": "...", "message": "...", "data": ...}   # data omitted if None
error:   {"status": "error",   "code": "...", "message": "...", "path": "..."} # + details[] on 422
```

## schemas/common.py

```python
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class EnvelopeResponse(BaseModel, Generic[T]):
    status: str = "success"
    code: str
    message: str
    data: Optional[T] = None

def success(code: str, message: str, data: Any = None) -> dict:
    body: dict[str, Any] = {"status": "success", "code": code, "message": message}
    if data is not None:
        body["data"] = data
    return body
```

## core/exceptions.py

```python
from __future__ import annotations

from typing import Any

import structlog
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.response_codes import ResponseCodes as RC

logger = structlog.get_logger()


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
    def __init__(self, message: str = "Invalid request", code: str | None = None, data: Any = None) -> None:
        super().__init__(message, status_code=400, code=code or RC.BAD_REQUEST, data=data)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", code: str | None = None) -> None:
        super().__init__(message, status_code=401, code=code or RC.UNAUTHORIZED)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", code: str | None = None) -> None:
        super().__init__(message, status_code=403, code=code or RC.FORBIDDEN)

class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", code: str | None = None) -> None:
        super().__init__(message, status_code=409, code=code or RC.CONFLICT)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.error("app_exception", path=request.url.path, method=request.method,
                 status_code=exc.status_code, code=exc.code, message=exc.message)
    body: dict[str, Any] = {"status": "error", "code": exc.code,
                            "message": exc.message, "path": request.url.path}
    if exc.data is not None:
        body["data"] = exc.data
    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"field": ".".join(str(loc) for loc in err["loc"]),
               "message": err["msg"], "type": err["type"]} for err in exc.errors()]
    logger.warning("validation_error", path=request.url.path, errors=errors)
    return JSONResponse(status_code=422, content={
        "status": "error", "code": RC.VALIDATION_ERROR, "message": "Validation error",
        "details": errors, "path": request.url.path})


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error("database_error", path=request.url.path, error=str(exc))
    if isinstance(exc, IntegrityError):
        # Unique/FK violations are driven by request data, not a server fault → 409, not 500.
        error_message, error_code = "Database integrity violation", RC.DATABASE_INTEGRITY_ERROR
        exc_str = str(exc).lower()
        if "duplicate key" in exc_str:
            error_message, error_code = "Duplicate record", RC.DUPLICATE_KEY
        elif "foreign key" in exc_str:
            error_message, error_code = "Invalid reference", RC.FOREIGN_KEY_ERROR
        return JSONResponse(status_code=409, content={
            "status": "error", "code": error_code, "message": error_message,
            "path": request.url.path})
    return JSONResponse(status_code=500, content={
        "status": "error", "code": RC.DATABASE_ERROR,
        "message": "Internal database error", "path": request.url.path})


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Wrap raw HTTPException (404, 405, ...) in the standard envelope."""
    code_map = {404: RC.NOT_FOUND, 405: RC.BAD_REQUEST, 401: RC.UNAUTHORIZED,
                403: RC.FORBIDDEN, 409: RC.CONFLICT}
    code = code_map.get(exc.status_code, RC.ERROR)
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(status_code=exc.status_code, content={
        "status": "error", "code": code, "message": message, "path": request.url.path})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", path=request.url.path,
                 error_type=type(exc).__name__, error=str(exc), exc_info=True)
    return JSONResponse(status_code=500, content={
        "status": "error", "code": RC.INTERNAL_SERVER_ERROR,
        "message": "Internal server error", "path": request.url.path})
```

## main.py registration

```python
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

Services raise the typed hierarchy; endpoints return `success(RC.X_CREATED, "...", data)`. The
`ResponseCodes` class is a flat registry of UPPER_SNAKE_CASE string constants grouped by domain.
