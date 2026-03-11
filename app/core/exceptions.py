import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.security import TokenError

logger = logging.getLogger("rpms")


class ErrorResponse(BaseModel):
    status_code: int
    detail: str
    error_code: str | None = None


class NotFoundException(Exception):
    def __init__(self, resource: str, resource_id: int | str):
        self.resource = resource
        self.resource_id = resource_id
        self.message = f"{resource} with id '{resource_id}' not found"


class ConflictException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class BadRequestException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ServiceUnavailableException(Exception):
    def __init__(self, detail: str = "Service temporarily unavailable"):
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                status_code=404,
                detail=exc.message,
                error_code="NOT_FOUND",
            ).model_dump(),
        )

    @app.exception_handler(ConflictException)
    async def conflict_handler(request: Request, exc: ConflictException):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                status_code=409,
                detail=exc.detail,
                error_code="CONFLICT",
            ).model_dump(),
        )

    @app.exception_handler(BadRequestException)
    async def bad_request_handler(request: Request, exc: BadRequestException):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                status_code=400,
                detail=exc.detail,
                error_code="BAD_REQUEST",
            ).model_dump(),
        )

    @app.exception_handler(ServiceUnavailableException)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableException):
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                status_code=503,
                detail=exc.detail,
                error_code="SERVICE_UNAVAILABLE",
            ).model_dump(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error("IntegrityError: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                status_code=409,
                detail="Data integrity violation",
                error_code="INTEGRITY_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        logger.error("OperationalError: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                status_code=503,
                detail="Database connection error",
                error_code="DB_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        logger.error("TimeoutError: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=504,
            content=ErrorResponse(
                status_code=504,
                detail="Request timed out",
                error_code="TIMEOUT",
            ).model_dump(),
        )

    @app.exception_handler(TokenError)
    async def token_error_handler(request: Request, exc: TokenError):
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                status_code=401,
                detail=exc.detail,
                error_code="AUTHENTICATION_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                status_code=500,
                detail="Internal server error",
                error_code="INTERNAL_ERROR",
            ).model_dump(),
        )
