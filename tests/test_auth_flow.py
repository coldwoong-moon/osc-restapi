import pytest
import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db


@pytest.fixture
def test_app(tmp_path):
    db_path = tmp_path / "test_auth.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    from app.db.base import Base
    import app.models.user  # noqa: F401
    import app.models.refresh_token  # noqa: F401
    Base.metadata.create_all(engine)

    TestSession = sessionmaker(bind=engine)

    with TestSession() as db:
        hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        db.execute(text(
            "INSERT INTO user (id, email, password, name, isEnabled) VALUES (1, 'test@test.com', :pw, 'Test User', 1)"
        ), {"pw": hashed})
        db.execute(text(
            "INSERT INTO authority (no, id, authorityName) VALUES (1, 'test@test.com', 'ROLE_USER')"
        ))
        db.commit()

    from app.main import create_app
    app = create_app()

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


class TestAuthFlow:
    def test_login_returns_tokens(self, test_app):
        resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["email"] == "test@test.com"

    def test_login_wrong_password(self, test_app):
        resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "wrong"})
        assert resp.status_code == 400

    def test_refresh_token_rotation(self, test_app):
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        tokens = login_resp.json()

        refresh_resp = test_app.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

    def test_old_refresh_token_rejected_after_rotation(self, test_app):
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        old_refresh = login_resp.json()["refresh_token"]

        test_app.post("/api/v1/refresh", json={"refresh_token": old_refresh})

        retry = test_app.post("/api/v1/refresh", json={"refresh_token": old_refresh})
        assert retry.status_code == 401

    def test_logout_invalidates_refresh_token(self, test_app):
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        tokens = login_resp.json()

        logout_resp = test_app.post(
            "/api/v1/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert logout_resp.status_code == 200

        refresh_resp = test_app.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh_resp.status_code == 401
