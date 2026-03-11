import time
import uuid

import jwt

from app.core.config import settings


class TokenError(Exception):
    def __init__(self, detail: str = "Invalid token"):
        self.detail = detail


def create_access_token(user_id: int, email: str, authorities: list[str]) -> str:
    now = int(time.time())
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": str(user_id),
        "email": email,
        "authorities": authorities,
        "type": "access",
        "iat": now,
        "exp": now + settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = int(time.time())
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")

    if int(time.time()) >= payload["exp"]:
        raise TokenError("Token has expired")

    payload["sub"] = int(payload["sub"])
    return payload
