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

class ValidationException(AppException):
    """Semantic validation a service performs AFTER pydantic accepted the shape
    (cross-field rules, business invariants). Pydantic's own rejection arrives as
    RequestValidationError and is handled separately."""
    def __init__(self, message: str = "Validation error", code: str | None = None, data: Any = None) -> None:
        super().__init__(message, status_code=422, code=code or RC.VALIDATION_ERROR, data=data)


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
        # NOTE: the sniffing below matches Postgres driver text. On another backend, or after a
        # driver reworded its message, it falls through to the generic integrity code — the 409 is
        # still correct, only the specific code is lost. Prefer `exc.orig.sqlstate` (23505 unique,
        # 23503 foreign key) when the driver exposes it, and keep this as the fallback.
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


async def too_deep_handler(request: Request, exc: RecursionError) -> JSONResponse:
    """A deeply-nested JSON body blows the parser's stack. Without this it reaches the
    catch-all and becomes a 500 — a 5xx caused purely by input. Measured: a 2 KB body of
    nested brackets returns 500 on a stock service, 400 with this handler registered."""
    logger.warning("payload_too_deep", path=request.url.path)
    return JSONResponse(status_code=400, content={
        "status": "error", "code": RC.PAYLOAD_TOO_DEEP,
        "message": "Request body nesting is too deep", "path": request.url.path})


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Wrap raw HTTPException (404, 405, ...) in the standard envelope. In a service that
    follows the 'never raise HTTPException directly' rule this only fires for framework-raised
    ones — 405 from routing, 404 for an unknown path — which is exactly why it must stay."""
    code_map = {404: RC.NOT_FOUND, 405: RC.BAD_REQUEST, 401: RC.UNAUTHORIZED,
                403: RC.FORBIDDEN, 409: RC.CONFLICT}
    code = code_map.get(exc.status_code, RC.ERROR)
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(status_code=exc.status_code, content={
        "status": "error", "code": code, "message": message, "path": request.url.path})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", path=request.url.path,
                 error_type=type(exc).__name__, error=str(exc), exc_info=True)
    # The real message is exposed ONLY in dev; production gets a fixed string so a stack
    # trace, SQL fragment or internal path can never leak through the catch-all.
    message = f"{type(exc).__name__}: {exc}" if settings.APP_ENV == "dev" else "Internal server error"
    return JSONResponse(status_code=500, content={
        "status": "error", "code": RC.INTERNAL_SERVER_ERROR,
        "message": message, "path": request.url.path})
```

## main.py registration

```python
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RecursionError, too_deep_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

`RecursionError` must be registered **before** the `Exception` catch-all reaches it — Starlette
resolves handlers by walking the exception's MRO, so the more specific class wins regardless of
registration order, but keeping the order explicit documents the intent.

Services raise the typed hierarchy; endpoints return `success(RC.X_CREATED, "...", data)`. The
`ResponseCodes` class is a flat registry of UPPER_SNAKE_CASE string constants grouped by domain.
