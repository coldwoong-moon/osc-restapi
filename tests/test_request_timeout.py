import asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.timeout import TimeoutMiddleware


def _make_app(timeout_seconds: float, exclude_paths: list[str] | None = None) -> FastAPI:
    app = FastAPI()

    kwargs = {"timeout_seconds": timeout_seconds}
    if exclude_paths is not None:
        kwargs["exclude_paths"] = exclude_paths

    app.add_middleware(TimeoutMiddleware, **kwargs)

    @app.get("/fast")
    async def fast():
        return {"status": "ok"}

    @app.get("/slow")
    async def slow():
        await asyncio.sleep(10)
        return {"status": "ok"}

    @app.get("/health/live")
    async def health_live():
        await asyncio.sleep(10)
        return {"status": "live"}

    @app.get("/health/ready")
    async def health_ready():
        await asyncio.sleep(10)
        return {"status": "ready"}

    return app


class TestRequestTimeout:

    def test_request_within_timeout(self):
        app = _make_app(timeout_seconds=5.0)
        client = TestClient(app)
        response = client.get("/fast")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_request_timeout_exceeded(self):
        app = _make_app(timeout_seconds=0.1)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/slow")
        assert response.status_code == 504

    def test_timeout_response_format(self):
        app = _make_app(timeout_seconds=0.1)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/slow")
        assert response.status_code == 504
        body = response.json()
        assert "detail" in body
        assert body["detail"] == "Gateway Timeout"

    def test_excluded_paths_no_timeout(self):
        app = _make_app(timeout_seconds=0.1)
        client = TestClient(app, raise_server_exceptions=False)
        response_live = client.get("/health/live")
        response_ready = client.get("/health/ready")
        assert response_live.status_code == 200
        assert response_ready.status_code == 200

    def test_custom_timeout_value(self):
        app = FastAPI()
        app.add_middleware(TimeoutMiddleware, timeout_seconds=0.2)

        @app.get("/borderline")
        async def borderline():
            await asyncio.sleep(0.5)
            return {"status": "ok"}

        @app.get("/quick")
        async def quick():
            return {"status": "ok"}

        client = TestClient(app, raise_server_exceptions=False)

        slow_response = client.get("/borderline")
        assert slow_response.status_code == 504

        fast_response = client.get("/quick")
        assert fast_response.status_code == 200
