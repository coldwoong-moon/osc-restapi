# JWT 인증 + N+1 최적화 + 포트폴리오 강화 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** JWT + Refresh Token 인증, N+1 쿼리 최적화, Q&A 문서를 추가하여 경력 면접용 기술 포트폴리오를 완성한다.

**Architecture:** FastAPI 의존성 주입 기반 인증. `app/core/security.py`에서 토큰 생성/검증, `app/api/deps.py`에서 `get_current_user` / `require_role` 의존성 제공. Refresh Token은 DB 저장 + 회전 방식. N+1 최적화는 `CRUDBase.get()`에 `options` 파라미터 추가.

**Tech Stack:** PyJWT, FastAPI Depends, SQLAlchemy (eager loading: joinedload/selectinload)

---

## Task 1: PyJWT 의존성 추가 + 설정 확장

**Files:**
- Modify: `requirements.txt`
- Modify: `app/core/config.py`

**Step 1: requirements.txt에 PyJWT 추가**

```
# requirements.txt 끝에 추가
PyJWT>=2.8.0
```

**Step 2: app/core/config.py에 JWT 설정 추가**

```python
# Settings 클래스에 추가
JWT_SECRET: str = "rpms-dev-secret-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 8
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
```

**Step 3: pip install 실행**

Run: `pip install PyJWT>=2.8.0`
Expected: Successfully installed PyJWT

**Step 4: Commit**

```bash
git add requirements.txt app/core/config.py
git commit -m "feat: add PyJWT dependency and JWT config settings"
```

---

## Task 2: security.py — JWT 토큰 생성/검증

**Files:**
- Create: `app/core/security.py`
- Create: `tests/test_jwt_token.py`

**Step 1: 토큰 생성/검증 테스트 작성**

```python
# tests/test_jwt_token.py
import time
import pytest
from app.core.security import create_access_token, create_refresh_token, decode_token, TokenError


class TestJWTToken:
    def test_create_access_token(self):
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

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
        # Advance time past expiry
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
```

**Step 2: 테스트 실행 — 실패 확인**

Run: `pytest tests/test_jwt_token.py -v`
Expected: FAIL (모듈 없음)

**Step 3: security.py 구현**

```python
# app/core/security.py
import time

import jwt

from app.core.config import settings


class TokenError(Exception):
    def __init__(self, detail: str = "Invalid token"):
        self.detail = detail


def create_access_token(user_id: int, email: str, authorities: list[str]) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "authorities": authorities,
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")
```

**Step 4: 테스트 실행 — 통과 확인**

Run: `pytest tests/test_jwt_token.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add app/core/security.py tests/test_jwt_token.py
git commit -m "feat: JWT token creation and validation with tests"
```

---

## Task 3: RefreshToken 모델

**Files:**
- Create: `app/models/refresh_token.py`
- Modify: `app/db/base.py` (import 추가)

**Step 1: RefreshToken 모델 작성**

```python
# app/models/refresh_token.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**Step 2: base.py에 import 추가**

`app/db/base.py`를 읽고, 다른 모델이 import되어 있다면 동일 패턴으로 RefreshToken도 추가.

**Step 3: Commit**

```bash
git add app/models/refresh_token.py app/db/base.py
git commit -m "feat: add RefreshToken model for token rotation"
```

---

## Task 4: auth.py 스키마 확장 + 엔드포인트 수정

**Files:**
- Modify: `app/schemas/auth.py`
- Modify: `app/api/v1/auth.py`
- Create: `tests/test_auth_flow.py`

**Step 1: 스키마 확장**

```python
# app/schemas/auth.py 에 추가

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: LoginResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
```

**Step 2: auth.py 인증 플로우 테스트 작성**

```python
# tests/test_auth_flow.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db


@pytest.fixture
def test_app():
    """SQLite 기반 테스트 앱"""
    engine = create_engine("sqlite:///test_auth.db")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    # user, authority, refresh_token 테이블에 시드 데이터 삽입
    with TestSession() as db:
        # BCrypt hash of "password123"
        import bcrypt
        hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        db.execute(text(
            "INSERT OR IGNORE INTO user (id, email, password, name, isEnabled) VALUES (1, 'test@test.com', :pw, 'Test User', 1)"
        ), {"pw": hashed})
        db.execute(text(
            "INSERT OR IGNORE INTO authority (no, id, authorityName) VALUES (1, 'test@test.com', 'ROLE_USER')"
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

    import os
    os.remove("test_auth.db")


class TestAuthFlow:
    def test_login_returns_tokens(self, test_app):
        resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@test.com"

    def test_login_wrong_password(self, test_app):
        resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "wrong"})
        assert resp.status_code == 400

    def test_refresh_token_rotation(self, test_app):
        # Login to get tokens
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        tokens = login_resp.json()

        # Use refresh token to get new tokens
        refresh_resp = test_app.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != tokens["refresh_token"]  # rotation

    def test_old_refresh_token_rejected_after_rotation(self, test_app):
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        old_refresh = login_resp.json()["refresh_token"]

        # Rotate
        test_app.post("/api/v1/refresh", json={"refresh_token": old_refresh})

        # Old token should be rejected
        retry = test_app.post("/api/v1/refresh", json={"refresh_token": old_refresh})
        assert retry.status_code == 401

    def test_logout_invalidates_refresh_token(self, test_app):
        login_resp = test_app.post("/api/v1/login", json={"email": "test@test.com", "password": "password123"})
        tokens = login_resp.json()

        # Logout
        logout_resp = test_app.post(
            "/api/v1/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert logout_resp.status_code == 200

        # Refresh should fail
        refresh_resp = test_app.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refresh_resp.status_code == 401
```

**Step 3: 테스트 실행 — 실패 확인**

Run: `pytest tests/test_auth_flow.py -v`
Expected: FAIL

**Step 4: auth.py 엔드포인트 수정**

`/login` 응답을 `TokenResponse`로 변경. `/refresh`, `/logout` 엔드포인트 추가.
- login: Access + Refresh 토큰 생성, Refresh 토큰 DB 저장
- refresh: 기존 Refresh 토큰 삭제 + 새 토큰 쌍 발급 (회전)
- logout: Refresh 토큰 DB에서 삭제

auth.py의 `text` import 누락도 함께 수정 (`from sqlalchemy import select, text`).

**Step 5: 테스트 실행 — 통과 확인**

Run: `pytest tests/test_auth_flow.py -v`
Expected: 5 passed

**Step 6: Commit**

```bash
git add app/schemas/auth.py app/api/v1/auth.py tests/test_auth_flow.py
git commit -m "feat: JWT login/refresh/logout with token rotation"
```

---

## Task 5: deps.py — 인증 의존성 (get_current_user, require_role)

**Files:**
- Create: `app/api/deps.py`
- Create: `tests/test_auth_deps.py`

**Step 1: 의존성 테스트 작성**

```python
# tests/test_auth_deps.py
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

    def test_expired_token_returns_401(self, app_with_protected_routes, monkeypatch):
        import time
        token = create_access_token(user_id=1, email="test@test.com", authorities=["ROLE_USER"])
        future = time.time() + 8 * 3600 + 60
        monkeypatch.setattr(time, "time", lambda: future)
        resp = app_with_protected_routes.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
```

**Step 2: 테스트 실행 — 실패 확인**

Run: `pytest tests/test_auth_deps.py -v`
Expected: FAIL

**Step 3: deps.py 구현**

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import TokenError, decode_token

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload


def require_role(role: str):
    def role_checker(user: dict = Depends(get_current_user)) -> dict:
        if role not in user.get("authorities", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{role}' required")
        return user
    return role_checker
```

**Step 4: 테스트 실행 — 통과 확인**

Run: `pytest tests/test_auth_deps.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add app/api/deps.py tests/test_auth_deps.py
git commit -m "feat: auth dependencies - get_current_user and require_role"
```

---

## Task 6: 기존 엔드포인트에 인증 적용

**Files:**
- Modify: `app/api/v1/projects.py` (예시)
- Modify: `app/api/v1/users.py` (예시)

**Step 1: 보호할 엔드포인트 선별**

인증이 필요한 엔드포인트에 `Depends(get_current_user)` 추가.
관리자 전용 엔드포인트(예: 사용자 생성/삭제)에 `Depends(require_role("ROLE_ADMIN"))` 추가.

패턴:
```python
from app.api.deps import get_current_user, require_role

@router.get("/projects", ...)
def list_projects(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    ...

@router.delete("/users/{user_id}", ...)
def delete_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("ROLE_ADMIN"))):
    ...
```

**Step 2: 기존 테스트가 깨지지 않는지 확인**

Run: `pytest tests/ -v --tb=short`

**Step 3: Commit**

```bash
git add app/api/v1/projects.py app/api/v1/users.py
git commit -m "feat: apply auth dependencies to protected endpoints"
```

---

## Task 7: N+1 쿼리 최적화 — CRUDBase 확장

**Files:**
- Modify: `app/crud/base.py`
- Create: `tests/test_eager_loading.py`

**Step 1: eager loading 테스트 작성**

```python
# tests/test_eager_loading.py
import pytest
from sqlalchemy import create_engine, event, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, joinedload, selectinload, DeclarativeBase


class TestBase(DeclarativeBase):
    pass


class Parent(TestBase):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    children = relationship("Child", back_populates="parent")


class Child(TestBase):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent.id"))
    name = Column(String(50))
    parent = relationship("Parent", back_populates="children")


class TestEagerLoading:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        db_path = tmp_path / "test.db"
        self.engine = create_engine(f"sqlite:///{db_path}")
        TestBase.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        # Seed data
        for i in range(5):
            p = Parent(id=i + 1, name=f"Parent {i}")
            self.db.add(p)
            for j in range(3):
                self.db.add(Child(parent_id=i + 1, name=f"Child {i}-{j}"))
        self.db.commit()
        self.query_count = 0
        event.listen(self.engine, "before_cursor_execute", self._count_queries)
        yield
        self.db.close()

    def _count_queries(self, conn, cursor, statement, parameters, context, executemany):
        self.query_count += 1

    def test_n_plus_1_without_eager(self):
        self.query_count = 0
        parents = self.db.query(Parent).all()
        for p in parents:
            _ = p.children  # triggers lazy load
        assert self.query_count > 1  # N+1 발생

    def test_joinedload_reduces_queries(self):
        self.query_count = 0
        parents = self.db.query(Parent).options(joinedload(Parent.children)).all()
        for p in parents:
            _ = p.children
        assert self.query_count == 1  # 단일 JOIN 쿼리

    def test_selectinload_reduces_queries(self):
        self.query_count = 0
        parents = self.db.query(Parent).options(selectinload(Parent.children)).all()
        for p in parents:
            _ = p.children
        assert self.query_count <= 2  # SELECT IN 최대 2쿼리
```

**Step 2: 테스트 실행 — 통과 확인**

Run: `pytest tests/test_eager_loading.py -v`
Expected: 3 passed

**Step 3: CRUDBase.get()에 options 파라미터 추가**

```python
# app/crud/base.py — get 메서드 수정
def get(self, db: Session, id: Any, options: list | None = None) -> ModelType | None:
    query = select(self.model).where(self.model.id == id)
    if options:
        query = query.options(*options)
    return db.scalar(query)
```

**Step 4: Commit**

```bash
git add app/crud/base.py tests/test_eager_loading.py
git commit -m "feat: add eager loading support to CRUDBase.get()"
```

---

## Task 8: 전역 에러 핸들러에 TokenError 추가

**Files:**
- Modify: `app/core/exceptions.py`

**Step 1: TokenError 핸들러 추가**

```python
# register_exception_handlers 내부에 추가
from app.core.security import TokenError

@app.exception_handler(TokenError)
async def token_error_handler(request: Request, exc: TokenError):
    return JSONResponse(
        status_code=401,
        content=ErrorResponse(
            status_code=401,
            detail=exc.detail,
            error_code="AUTHENTICATION_ERROR",
        ).model_dump(),
    )
```

**Step 2: Commit**

```bash
git add app/core/exceptions.py
git commit -m "feat: add TokenError to global exception handlers"
```

---

## Task 9: Q&A 문서 작성

**Files:**
- Create: `docs/10_인증_설계.md`
- Create: `docs/11_쿼리_최적화_적용.md`

**Step 1: docs/10_인증_설계.md 작성**

Q&A 주제:
- Q: 왜 JWT를 선택했는가? / A: 서버 무상태, Redis 불필요, WinForms 호환
- Q: 왜 HS256인가? / A: 단일 서버에서 비대칭 키 불필요, 성능 우위
- Q: Refresh Token을 왜 DB에 저장하는가? / A: 즉시 무효화, 토큰 회전으로 탈취 감지
- Q: 토큰 만료 시간 8시간의 근거는? / A: 사내 시스템, 근무 시간 기준
- Q: 권한 체크를 어떻게 구현했는가? / A: FastAPI Depends 패턴
- Q: 테스트 결과는? / A: 테스트 수 및 시나리오 요약

**Step 2: docs/11_쿼리_최적화_적용.md 작성**

Q&A 주제:
- Q: 왜 상세 조회에만 적용했는가? / A: 목록은 기본 정보만, 상세에서만 관계 필요
- Q: joinedload vs selectinload 선택 기준은? / A: 1:1은 joinedload, 1:N은 selectinload
- Q: CRUDBase 확장 방식을 선택한 이유는? / A: 기존 코드 최소 변경, 옵션 파라미터
- Q: 테스트 결과는? / A: N+1 발생 vs eager loading 쿼리 수 비교

**Step 3: Commit**

```bash
git add docs/10_인증_설계.md docs/11_쿼리_최적화_적용.md
git commit -m "docs: add Q&A docs for JWT auth design and query optimization"
```

---

## Task 10: 전체 테스트 실행 및 최종 확인

**Step 1: 전체 테스트 실행**

Run: `pytest tests/ -v --tb=short`
Expected: 전체 pass (기존 57 + 신규 ~17 = 74+ tests)

**Step 2: Swagger UI 확인**

Run: `uvicorn app.main:app --reload`
브라우저에서 `/docs` 접속, 인증 플로우 확인.

**Step 3: 최종 Commit**

```bash
git add -A
git commit -m "feat: complete JWT auth + N+1 optimization + portfolio docs"
```
