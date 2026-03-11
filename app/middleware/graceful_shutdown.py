import asyncio
import logging
import threading

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("rpms")


class GracefulShutdownMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, drain_timeout: float = 30.0):
        super().__init__(app)
        self._shutting_down = False
        self._active_requests = 0
        self._lock = threading.Lock()
        self._drain_timeout = drain_timeout

    def initiate_shutdown(self):
        self._shutting_down = True

    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down

    @property
    def active_requests(self) -> int:
        return self._active_requests

    async def wait_for_drain(self) -> bool:
        elapsed = 0.0
        interval = 0.5
        while elapsed < self._drain_timeout:
            if self._active_requests == 0:
                logger.info("All in-flight requests drained.")
                return True
            await asyncio.sleep(interval)
            elapsed += interval
        logger.warning(
            "Drain timeout (%.1fs) reached with %d active requests.",
            self._drain_timeout,
            self._active_requests,
        )
        return False

    async def dispatch(self, request: Request, call_next):
        if self._shutting_down and request.url.path != "/health/live":
            return JSONResponse(
                status_code=503,
                content={"detail": "Service Unavailable: server is shutting down"},
            )

        with self._lock:
            self._active_requests += 1
        try:
            return await call_next(request)
        finally:
            with self._lock:
                self._active_requests -= 1
