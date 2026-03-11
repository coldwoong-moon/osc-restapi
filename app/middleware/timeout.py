import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        timeout_seconds: float = 30.0,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
        self.exclude_paths: list[str] = exclude_paths if exclude_paths is not None else [
            "/health/live",
            "/health/ready",
        ]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={"detail": "Gateway Timeout"},
            )
