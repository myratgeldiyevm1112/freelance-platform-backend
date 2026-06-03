from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from app.domain.exceptions import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
    AppError,
    UnauthorizedError,
)

logger = logging.getLogger("freelance_platform")

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        logger.warning(f"NotFound: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        logger.warning(f"Forbidden: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=403, content={"detail": exc.message})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        logger.warning(f"Conflict: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.error(f"AppError: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        logger.warning(f"Unauthorized: {request.method} {request.url.path} - {exc.message}")
        return JSONResponse(status_code=401, content={"detail": exc.message})