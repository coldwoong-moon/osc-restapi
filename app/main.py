import logging
import time

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.circuit_breaker import CircuitBreakerMiddleware
from app.middleware.graceful_shutdown import GracefulShutdownMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.timeout import TimeoutMiddleware

logger = logging.getLogger("rpms")
logging.basicConfig(level=logging.INFO)

HEALTH_PATHS = ["/health/live", "/health/ready", "/health"]


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GracefulShutdownMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=100,
        window_seconds=60,
        exclude_paths=HEALTH_PATHS,
    )
    app.add_middleware(
        TimeoutMiddleware,
        timeout_seconds=30.0,
        exclude_paths=HEALTH_PATHS,
    )
    app.add_middleware(
        CircuitBreakerMiddleware,
        failure_threshold=5,
        recovery_timeout=30,
        half_open_max_calls=3,
        exclude_paths=HEALTH_PATHS,
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response

    register_exception_handlers(app)

    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
