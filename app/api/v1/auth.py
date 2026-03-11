import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import Authority, User
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, RefreshRequest, TokenRefreshResponse

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="로그인")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise NotFoundException("User", payload.email)

    if not user.isEnabled:
        raise BadRequestException("Account is disabled")

    stored_password = user.password if isinstance(user.password, bytes) else user.password.encode("utf-8")
    if not _verify_password(payload.password, stored_password):
        raise BadRequestException("Invalid password")

    authorities = _get_user_authorities(db, user.email)

    access_token = create_access_token(user.id, user.email, authorities)
    refresh_token = create_refresh_token(user.id)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(db_refresh)
    db.commit()

    user_response = LoginResponse.model_validate(user)
    user_response.authorities = authorities

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=user_response,
    )


@router.post("/refresh", response_model=TokenRefreshResponse, summary="토큰 갱신")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(payload.refresh_token)
    except TokenError as e:
        raise HTTPException(status_code=401, detail=e.detail)

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = token_data["sub"]

    db_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token == payload.refresh_token,
            RefreshToken.user_id == user_id,
        )
    )
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token not found or already used")

    db.delete(db_token)
    db.flush()

    user = db.get(User, user_id)
    if not user:
        db.rollback()
        raise HTTPException(status_code=401, detail="User not found")

    authorities = _get_user_authorities(db, user.email)
    new_access_token = create_access_token(user.id, user.email, authorities)
    new_refresh_token = create_refresh_token(user.id)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_refresh = RefreshToken(user_id=user.id, token=new_refresh_token, expires_at=expires_at)
    db.add(new_db_refresh)
    db.commit()

    return TokenRefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )


@router.post("/logout", summary="로그아웃")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    db_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    )
    if db_token:
        db.delete(db_token)
        db.commit()

    return {"message": "Logged out successfully"}


def _verify_password(plain_password: str, hashed_password: bytes) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    except Exception:
        return False


def _get_user_authorities(db: Session, email: str) -> list[str]:
    rows = db.execute(
        text("SELECT authorityName FROM authority WHERE id = :email"),
        {"email": email},
    ).fetchall()
    return [row[0] for row in rows]
