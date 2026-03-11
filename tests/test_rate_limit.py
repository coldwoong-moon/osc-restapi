import time
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.rate_limit import RateLimitMiddleware


def make_app(max_requests: int = 5, window_seconds: int = 60) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    @app.get("/health/live")
    async def health_live():
        return {"status": "alive"}

    @app.get("/health/ready")
    async def health_ready():
        return {"status": "ready"}

    return app


class TestRateLimit:
    def test_request_within_limit(self):
        client = TestClient(make_app(max_requests=5))
        for _ in range(5):
            response = client.get("/ping")
            assert response.status_code == 200

    def test_rate_limit_exceeded(self):
        client = TestClient(make_app(max_requests=3))
        for _ in range(3):
            client.get("/ping")
        response = client.get("/ping")
        assert response.status_code == 429
        assert response.json()["detail"] == "Too Many Requests"

    def test_retry_after_header(self):
        client = TestClient(make_app(max_requests=2, window_seconds=30))
        for _ in range(2):
            client.get("/ping")
        response = client.get("/ping")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        retry_after = int(response.headers["Retry-After"])
        assert 0 < retry_after <= 30

    def test_different_ips_independent(self):
        app = make_app(max_requests=2)
        client = TestClient(app)

        for _ in range(2):
            client.get("/ping", headers={"X-Forwarded-For": "1.2.3.4"})

        over_limit = client.get("/ping", headers={"X-Forwarded-For": "1.2.3.4"})
        assert over_limit.status_code == 429

        other_ip = client.get("/ping", headers={"X-Forwarded-For": "9.9.9.9"})
        assert other_ip.status_code == 200

    def test_window_expiry(self, monkeypatch):
        app = make_app(max_requests=3, window_seconds=60)
        client = TestClient(app)

        fake_now = 1_000_000.0

        monkeypatch.setattr(time, "time", lambda: fake_now)
        for _ in range(3):
            client.get("/ping")

        exceeded = client.get("/ping")
        assert exceeded.status_code == 429

        fake_now += 61.0
        monkeypatch.setattr(time, "time", lambda: fake_now)

        response = client.get("/ping")
        assert response.status_code == 200

    def test_excluded_paths(self):
        client = TestClient(make_app(max_requests=1))
        client.get("/ping")

        over_limit = client.get("/ping")
        assert over_limit.status_code == 429

        live = client.get("/health/live")
        assert live.status_code == 200

        ready = client.get("/health/ready")
        assert ready.status_code == 200
