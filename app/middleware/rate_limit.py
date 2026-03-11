import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exclude_paths: list[str] = exclude_paths if exclude_paths is not None else [
            "/health/live",
            "/health/ready",
        ]
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self._windows[ip]

        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        if len(timestamps) >= self.max_requests:
            oldest = timestamps[0]
            retry_after = int(oldest - window_start)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)
        return await call_next(request)
