"""
Custom exceptions and centralised error handlers (guide §5.1 core/exceptions.py).
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class Doc2DrawError(Exception):
    """Base application error carrying an HTTP status code."""

    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(Doc2DrawError):
    status_code = 404
    detail = "Resource not found"


class UnsupportedMediaError(Doc2DrawError):
    status_code = 415
    detail = "Unsupported media type"


class PayloadTooLargeError(Doc2DrawError):
    status_code = 413
    detail = "File too large"


class QuotaExceededError(Doc2DrawError):
    status_code = 429
    detail = "Monthly quota exceeded"


class AuthError(Doc2DrawError):
    status_code = 401
    detail = "Not authenticated"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Doc2DrawError)
    async def _handle(request: Request, exc: Doc2DrawError):  # noqa: ANN001
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
