import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.api.deps import get_current_user, require_role


@pytest.fixture
def app_with_protected_routes():
    app = FastAPI()

    @app.get("/me")
    def me(user=Depends(get_current_user)):
        return {"user_id": user["sub"], "email": user["email"]}

    @app.get("/admin-only")
    def admin_only(user=Depends(require_role("ROLE_ADMIN"))):
        return {"message": "admin access granted"}

    return TestClient(app)


class TestAuthDeps:
    def test_valid_token_extracts_user(self, app_with_protected_routes):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        resp = app_with_protected_routes.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == 1

    def test_missing_token_returns_401(self, app_with_protected_routes):
        resp = app_with_protected_routes.get("/me")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, app_with_protected_routes):
        resp = app_with_protected_routes.get("/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401

    def test_role_check_passes(self, app_with_protected_routes):
        token = create_access_token(user_id=1, email="admin@test.com", authorities=["ROLE_ADMIN"])
        resp = app_with_protected_routes.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_role_check_fails_wrong_role(self, app_with_protected_routes):
        token = create_access_token(user_id=1, email="user@test.com", authorities=["ROLE_USER"])
        resp = app_with_protected_routes.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_refresh_token_rejected_for_api_access(self, app_with_protected_routes):
        from app.core.security import create_refresh_token
        token = create_refresh_token(user_id=1)
        resp = app_with_protected_routes.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
