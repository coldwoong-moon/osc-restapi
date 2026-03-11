import time
import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from app.middleware.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerMiddleware,
    CircuitState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app(
    failure_threshold: int = 3,
    recovery_timeout: int = 30,
    half_open_max_calls: int = 2,
    exclude_paths: list[str] | None = None,
) -> tuple[FastAPI, CircuitBreaker]:
    """Return (app, circuit_breaker) so tests can inspect state directly."""
    app = FastAPI()

    cb = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        half_open_max_calls=half_open_max_calls,
    )

    # Patch the middleware to use the pre-created CircuitBreaker instance
    class _PreconfiguredMiddleware(CircuitBreakerMiddleware):
        def __init__(self, inner_app, **kwargs):
            super().__init__(inner_app, **kwargs)
            self.circuit_breaker = cb  # replace with shared instance

    app.add_middleware(
        _PreconfiguredMiddleware,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        half_open_max_calls=half_open_max_calls,
        exclude_paths=exclude_paths,
    )

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/fail")
    async def fail():
        return Response(status_code=500)

    @app.get("/health/live")
    async def health_live():
        return {"status": "alive"}

    return app, cb


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCircuitBreaker:

    def test_circuit_closed_normal_operation(self):
        app, cb = _make_app(failure_threshold=3)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(5):
                resp = client.get("/ok")
                assert resp.status_code == 200
            assert cb.state == CircuitState.CLOSED

    def test_circuit_opens_after_failures(self):
        app, cb = _make_app(failure_threshold=3)
        with TestClient(app, raise_server_exceptions=False) as client:
            assert cb.state == CircuitState.CLOSED
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN

    def test_circuit_open_returns_503(self):
        app, cb = _make_app(failure_threshold=3)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN
            resp = client.get("/ok")
            assert resp.status_code == 503
            assert resp.json()["detail"] == "Service Unavailable"

    def test_circuit_transitions_to_half_open(self, monkeypatch):
        app, cb = _make_app(failure_threshold=3, recovery_timeout=30)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN

            # Advance time past recovery_timeout
            original_time = time.time
            monkeypatch.setattr(time, "time", lambda: original_time() + 31)

            assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_success_closes_circuit(self, monkeypatch):
        app, cb = _make_app(failure_threshold=3, recovery_timeout=30, half_open_max_calls=2)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN

            original_time = time.time
            monkeypatch.setattr(time, "time", lambda: original_time() + 31)

            # Confirm transition
            assert cb.state == CircuitState.HALF_OPEN

            # half_open_max_calls=2 successes should close the circuit
            for _ in range(2):
                resp = client.get("/ok")
                assert resp.status_code == 200

            assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self, monkeypatch):
        app, cb = _make_app(failure_threshold=3, recovery_timeout=30, half_open_max_calls=2)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN

            original_time = time.time
            monkeypatch.setattr(time, "time", lambda: original_time() + 31)

            assert cb.state == CircuitState.HALF_OPEN

            # One failure in HALF_OPEN should reopen the circuit
            client.get("/fail")
            assert cb.state == CircuitState.OPEN

    def test_excluded_paths_bypass(self):
        app, cb = _make_app(failure_threshold=3)
        with TestClient(app, raise_server_exceptions=False) as client:
            for _ in range(3):
                client.get("/fail")
            assert cb.state == CircuitState.OPEN

            # /health/live is excluded — must succeed even when circuit is OPEN
            resp = client.get("/health/live")
            assert resp.status_code == 200
            assert resp.json()["status"] == "alive"
