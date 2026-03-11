import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.health import router as health_router
from app.db.session import get_db
from app.middleware.graceful_shutdown import GracefulShutdownMiddleware


# ---------------------------------------------------------------------------
# SQLite in-memory DB helpers
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite://"

_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def override_get_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_app():
    app = FastAPI()
    app.include_router(health_router)
    app.dependency_overrides[get_db] = override_get_db
    return app


def make_app_with_shutdown():
    """Return (app, middleware_instance) so the caller can call initiate_shutdown()."""
    app = FastAPI()
    app.include_router(health_router)
    app.dependency_overrides[get_db] = override_get_db

    # Instantiate middleware directly so we hold a reference before Starlette wraps it
    mw = GracefulShutdownMiddleware(app)  # wraps the inner app
    return mw, app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealthEndpoints:
    def test_liveness_always_ok(self):
        client = TestClient(make_app())
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    def test_readiness_with_db(self):
        client = TestClient(make_app())
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    def test_readiness_without_db(self, monkeypatch):
        def broken_db():
            db = _SessionLocal()
            monkeypatch.setattr(
                db,
                "execute",
                lambda *a, **kw: (_ for _ in ()).throw(Exception("DB down")),
            )
            try:
                yield db
            finally:
                db.close()

        app = FastAPI()
        app.include_router(health_router)
        app.dependency_overrides[get_db] = broken_db
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["database"] == "disconnected"

    def test_health_backward_compat(self):
        client = TestClient(make_app())
        ready_resp = client.get("/health/ready")
        health_resp = client.get("/health")
        assert health_resp.status_code == ready_resp.status_code
        assert health_resp.json() == ready_resp.json()


class TestGracefulShutdown:
    def test_graceful_shutdown_rejects_new(self):
        mw, inner_app = make_app_with_shutdown()
        # TestClient receives the middleware as the ASGI app
        client = TestClient(mw, raise_server_exceptions=False)

        # Before shutdown: normal request succeeds
        resp = client.get("/health/ready")
        assert resp.status_code == 200

        mw.initiate_shutdown()

        resp = client.get("/health/ready")
        assert resp.status_code == 503
        assert "shutting down" in resp.json()["detail"]

    def test_graceful_shutdown_allows_health_live(self):
        mw, inner_app = make_app_with_shutdown()
        client = TestClient(mw, raise_server_exceptions=False)

        mw.initiate_shutdown()

        resp = client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json() == {"status": "alive"}
