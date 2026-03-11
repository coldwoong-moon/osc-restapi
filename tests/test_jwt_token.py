import time
import pytest
from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError


class TestJWTToken:
    def test_create_access_token(self):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_decode_valid_access_token(self):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        payload = decode_token(token)
        assert payload["sub"] == 1
        assert payload["email"] == "test@test.com"
        assert payload["authorities"] == ["ROLE_USER"]
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token(user_id=1)
        payload = decode_token(token)
        assert payload["sub"] == 1
        assert payload["type"] == "refresh"

    def test_expired_token_rejected(self, monkeypatch):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        future = time.time() + 8 * 3600 + 60
        monkeypatch.setattr(time, "time", lambda: future)
        with pytest.raises(TokenError, match="expired"):
            decode_token(token)

    def test_invalid_token_rejected(self):
        with pytest.raises(TokenError):
            decode_token("invalid.token.string")

    def test_tampered_token_rejected(self):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(TokenError):
            decode_token(tampered)
