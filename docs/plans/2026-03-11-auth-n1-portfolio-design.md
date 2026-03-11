# 설계: JWT 인증 + N+1 최적화 + 포트폴리오 강화

> 2026-03-11 | 경력 면접용 기술 포트폴리오 목적

---

## 배경

FastAPI 전환 프로젝트에서 백엔드 전반(아키텍처, DB, 운영)의 균형 잡힌 역량을 보여주기 위한 구현.
기존 Q&A 문서 9개 + 테스트 57개 기반 위에 인증/최적화/문서화를 추가한다.

## 접근 방식

**의사결정 기록 중심 (방안 2)**: 기능 구현 + 각 결정의 "왜?"를 Q&A 문서로 남김.

---

## 1. JWT 인증 시스템

### 구조

```
app/core/security.py     — JWT 토큰 생성/검증, 비밀키 관리
app/api/v1/auth.py       — POST /login (수정), POST /refresh, POST /logout
app/api/deps.py          — get_current_user(), require_role() 의존성
app/models/refresh_token.py — RefreshToken DB 모델
app/schemas/auth.py      — TokenResponse, RefreshRequest 추가
```

### 설계 결정

| 항목 | 선택 | 근거 |
|------|------|------|
| 알고리즘 | HS256 | 단일 서버, 비대칭 키 불필요 |
| Access Token | 8시간, JWT body | 사내 시스템 편의성 |
| Refresh Token | 30일, DB 저장 | 즉시 무효화 가능, 토큰 회전으로 탈취 방지 |
| 권한 체크 | `Depends(require_role("ROLE_ADMIN"))` | FastAPI 의존성 주입 패턴 활용 |
| 비밀키 | 환경변수 `RPMS_JWT_SECRET` | 코드에 하드코딩 방지 |

### 인증 플로우

```
[로그인] POST /login → Access + Refresh 토큰 반환
[API 호출] Authorization: Bearer {access_token}
[갱신] POST /refresh → 새 Access + 새 Refresh (회전)
[로그아웃] POST /logout → Refresh 토큰 DB에서 삭제
```

---

## 2. N+1 쿼리 최적화

### 적용 범위

상세 조회 엔드포인트에서만 eager loading 적용:

| 엔드포인트 | 관계 | 전략 |
|-----------|------|------|
| GET /projects/{id} | Project → ProjectModel | `joinedload` |
| GET /assemblies/{id} | Assembly → Parts | `selectinload` |
| GET /users/{id} | User → Authority | `joinedload` |

### 구현 패턴

- `CRUDBase.get()` 메서드에 `options` 파라미터 추가
- 각 라우터의 상세 조회에서 eager loading 옵션 전달
- 목록 조회는 기본 정보만 반환 (관계 데이터 미포함)

---

## 3. 포트폴리오 강화

| 항목 | 내용 |
|------|------|
| Swagger 강화 | 엔드포인트별 description, response_model, 에러 응답 예시 |
| 문서 추가 | `docs/10_인증_설계.md`, `docs/11_쿼리_최적화_적용.md` (Q&A 형식) |
| 테스트 | JWT 인증 플로우 테스트, 권한 체크 테스트, eager loading 쿼리 수 비교 테스트 |

---

## 테스트 계획

### JWT 인증 (8+ 테스트)
- 로그인 성공/실패
- 유효한 토큰으로 보호된 API 접근
- 만료된 토큰 거부
- Refresh 토큰으로 Access 토큰 갱신
- Refresh 토큰 회전 (이전 토큰 무효화)
- 로그아웃 후 Refresh 토큰 무효화
- 역할 기반 접근 제어 (ROLE_ADMIN only 엔드포인트)
- 잘못된 토큰 형식 거부

### N+1 최적화 (3+ 테스트)
- eager loading 적용 전/후 쿼리 수 비교
- joinedload vs selectinload 동작 확인
- 목록 조회에서 N+1 미발생 확인
