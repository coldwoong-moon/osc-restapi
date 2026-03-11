import time
import threading
from enum import Enum
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._lock = threading.Lock()
        self._failure_count = 0
        self._opened_at: float | None = None
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._opened_at is not None and (
                    time.time() - self._opened_at >= self.recovery_timeout
                ):
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self._half_open_successes = 0
            return self._state

    def allow_request(self) -> bool:
        current = self.state
        if current == CircuitState.CLOSED:
            return True
        if current == CircuitState.OPEN:
            return False
        # HALF_OPEN
        with self._lock:
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

    def record_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._opened_at = None
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = time.time()
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    self._opened_at = time.time()


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            half_open_max_calls=half_open_max_calls,
        )
        self.exclude_paths: list[str] = (
            exclude_paths if exclude_paths is not None else ["/health/live"]
        )

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        if not self.circuit_breaker.allow_request():
            return JSONResponse(
                status_code=503,
                content={"detail": "Service Unavailable"},
            )

        response = await call_next(request)

        if response.status_code >= 500:
            self.circuit_breaker.record_failure()
        else:
            self.circuit_breaker.record_success()

        return response
