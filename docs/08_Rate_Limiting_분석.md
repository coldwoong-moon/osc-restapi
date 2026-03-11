# Rate Limiting 분석

> 이 문서는 프로덕션 강화 작업의 일환으로 구현한 Rate Limiting 미들웨어의
> 설계 결정 과정과 검증 결과를 Q&A 형식으로 정리한 것입니다.

---

## Q: 왜 Rate Limiting을 도입했는가?

A: 세 가지 실서비스 운영 리스크에 대응하기 위해 도입했다.

1. **API Abuse 방지**: 악의적이거나 잘못 구현된 클라이언트가 루프를 돌며
   과도한 요청을 보낼 경우, DB 커넥션 풀이 소진되어 정상 사용자까지 서비스 불가 상태가 된다.

2. **DDoS 완화**: 분산 공격까지는 방어하지 못하더라도, 단일 IP 또는
   소수 IP에서 오는 과부하 트래픽을 차단하면 서버 자원이 보호된다.

3. **공정한 리소스 분배**: 한 명의 사용자가 전체 커넥션 풀과 CPU를
   독점하는 상황을 막고, 동시 접속자들이 균등하게 서비스를 받을 수 있도록 한다.

---

## Q: 어떤 목표를 가지고 진행했는가?

A: 다음 두 가지를 핵심 목표로 설정했다.

1. **IP 기반 Sliding Window 제한**: 특정 IP 주소를 식별자로 사용하여
   지정된 시간 창(window) 안에서의 요청 횟수를 추적하고, 초과 시 차단한다.

2. **표준 HTTP 응답 준수**: 제한 초과 시 `429 Too Many Requests`를 반환하고,
   `Retry-After` 헤더에 다시 요청 가능한 시점까지 남은 초(秒)를 포함하여
   클라이언트가 자동으로 재시도 타이밍을 조절할 수 있도록 한다.

---

## Q: 어떤 알고리즘을 선택했는가?

A: **Sliding Window Log** 방식을 선택했다. 선택 과정에서 세 가지 알고리즘을 비교했다.

### 비교 분석

| 항목 | Fixed Window | Token Bucket | Sliding Window Log |
|------|-------------|-------------|-------------------|
| 구현 복잡도 | 낮음 | 중간 | 중간 |
| 경계 버스트 허용 | **있음** (윈도우 전환 시 2배 허용) | 없음 | 없음 |
| 메모리 사용 | 낮음 (카운터만) | 낮음 (토큰만) | 중간 (타임스탬프 목록) |
| 정밀도 | 낮음 | 높음 | **높음** |
| 분산 환경 확장 | 쉬움 | 어려움 | 쉬움 (Redis Sorted Set) |
| Retry-After 계산 | 부정확 | 추정 필요 | **정확** |

#### Fixed Window의 한계
윈도우 경계에서 두 배 버스트가 허용된다.
예를 들어 60초 창에서 100req 제한이라면,
59초에 100개, 61초에 100개 — 즉 2초 동안 200개 요청이 허용된다.
이는 의도한 제한을 초과하는 허점이 된다.

#### Token Bucket의 한계
리필 속도와 버킷 크기 두 파라미터를 동시에 관리해야 하고,
`Retry-After` 계산이 복잡하다. 또한 단기 버스트를 허용하므로
API 남용 패턴에 취약할 수 있다.

#### Sliding Window Log 선택 이유
- 요청 타임스탬프 목록을 보관하여 **임의의 시점을 기준으로 정확한 카운트**가 가능하다.
- 오래된 타임스탬프를 제거하면 메모리가 자동으로 정리된다.
- `Retry-After` 값을 `가장 오래된 타임스탬프 + window` 로 정확히 계산할 수 있다.
- Redis Sorted Set으로 이전하면 분산 환경에서도 동일한 로직을 재사용할 수 있다.

### 핵심 구현 로직

```python
class SlidingWindowRateLimiter:
    def __init__(self):
        self._store: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        async with self._lock:
            now = time.time()
            window_start = now - window
            timestamps = self._store[key]

            # 윈도우 밖의 오래된 요청 제거
            self._store[key] = [t for t in timestamps if t > window_start]

            if len(self._store[key]) >= limit:
                # Retry-After: 가장 오래된 요청이 윈도우를 벗어나는 시점
                retry_after = int(self._store[key][0] + window - now) + 1
                return False, retry_after

            self._store[key].append(now)
            return True, 0
```

---

## Q: Rate Limit 설정 기준은?

A: 엔드포인트의 성격과 잠재적 남용 위험도에 따라 차등 적용했다.

| 엔드포인트 유형 | 제한 | 윈도우 | 선택 근거 |
|----------------|------|--------|-----------|
| 일반 API (`/api/v1/*`) | 100 req | 60초 | 초당 약 1.67req — 일반적인 UI 조작에 충분 |
| 로그인 (`/login`) | 5 req | 60초 | 브루트포스 공격 방지 |
| 헬스체크 (`/health`) | 적용 제외 | — | 모니터링 시스템이 자주 호출함 |

#### 설정 근거 상세

**일반 API 100req/60s**:
- 사용자가 빠르게 화면을 전환하며 조회할 경우 최대 초당 2-3개 요청이 발생할 수 있다.
- 100req/60s(초당 1.67개)는 정상 사용 패턴을 포용하면서 과도한 루프를 차단한다.
- 향후 측정된 트래픽을 기반으로 상향 조정 가능하다.

**로그인 5req/60s**:
- 비밀번호 브루트포스 공격은 초당 수백~수천 번 시도한다.
- 5회 제한은 오타로 인한 재시도를 허용하면서 자동화된 공격을 효과적으로 차단한다.
- 계정 잠금(Account Lockout) 정책과 함께 사용하면 더욱 강력하다.

---

## Q: 분산 환경에서의 한계는?

A: 현재 구현은 **단일 프로세스 인메모리** 방식이므로 수평 확장 시 한계가 있다.

### 현재 방식의 제약

```
[사용자 IP: 1.2.3.4]
       |
  ┌────┴────┐
  │  인스턴스 A│  ← 요청 60개 기록
  └─────────┘
  ┌─────────┐
  │  인스턴스 B│  ← 요청 60개 기록 (A와 공유 안 됨)
  └─────────┘

결과: 실제로는 120개 요청이 처리되지만, 각 인스턴스는 제한을 적용하지 않음
```

인스턴스 A와 B가 각자 독립된 카운트를 유지하므로,
로드 밸런서가 요청을 분산하면 각 인스턴스는 제한 미만이라 판단하여 처리한다.
결과적으로 인스턴스 수만큼 실제 허용량이 배증된다.

### Redis 기반 분산 확장 방안

```python
# 현재: 인메모리 딕셔너리
self._store: dict[str, list[float]] = defaultdict(list)

# 확장: Redis Sorted Set
await redis.zadd(key, {str(now): now})           # 요청 추가
await redis.zremrangebyscore(key, 0, window_start)  # 오래된 요청 제거
count = await redis.zcard(key)                    # 현재 카운트 조회
await redis.expire(key, window)                   # TTL 설정
```

Redis Sorted Set에서 타임스탬프를 score로 사용하면
인메모리 로직과 동일한 알고리즘을 분산 환경에서 원자적으로 실행할 수 있다.
`MULTI/EXEC` 또는 Lua 스크립트로 조회-추가-제거를 원자적 트랜잭션으로 묶어야 한다.

| 항목 | 인메모리 (현재) | Redis (확장 후) |
|------|---------------|----------------|
| 정확도 | 단일 인스턴스 내 정확 | 다중 인스턴스 전체 정확 |
| 재시작 시 상태 | 소실 | 유지 |
| 구현 복잡도 | 낮음 | 중간 |
| 추가 인프라 | 불필요 | Redis 필요 |
| 권장 시점 | 단일 인스턴스 운영 중 | 인스턴스 2개 이상 운영 시 |

---

## Q: 테스트 결과는?

A: 총 6개 테스트를 작성하여 모두 통과했다.

```
tests/test_rate_limiting.py::test_requests_within_limit        PASSED
tests/test_rate_limiting.py::test_rate_limit_exceeded          PASSED
tests/test_rate_limiting.py::test_retry_after_header           PASSED
tests/test_rate_limiting.py::test_rate_limit_window_resets     PASSED
tests/test_rate_limiting.py::test_different_ips_independent    PASSED
tests/test_rate_limiting.py::test_health_endpoint_excluded     PASSED
```

### 주요 시나리오별 검증

**시나리오 1 — 정상 범위 내 요청**: 제한(100) 미만의 요청은 모두 `200 OK`를 반환하고,
미들웨어가 요청을 통과시키는지 확인했다.

**시나리오 2 — 제한 초과**: 101번째 요청부터 `429 Too Many Requests`가 반환되고,
응답 본문에 `{"detail": "요청이 너무 많습니다..."}` 메시지가 포함되는지 검증했다.

**시나리오 3 — Retry-After 헤더**: `429` 응답에 `Retry-After` 헤더가 존재하고,
값이 양의 정수(초)인지 확인했다. 헤더 값대로 대기 후 재요청이 성공하는지도 검증했다.

**시나리오 4 — 윈도우 리셋**: 윈도우 시간(60초)이 경과한 후 요청 카운트가
리셋되어 다시 정상 응답을 받는지 확인했다. 테스트에서는 짧은 윈도우(1초)를 사용하여
실시간으로 검증했다.

**시나리오 5 — IP 독립성**: IP A가 제한을 초과한 상태에서 IP B의 요청은
정상적으로 처리되는지 확인했다. 서로 다른 IP의 카운트가 격리되어 있음을 보장한다.

**시나리오 6 — 헬스체크 제외**: `/health` 엔드포인트는 Rate Limit이 적용되지 않으므로,
제한을 초과한 IP라도 `200 OK`를 반환하는지 확인했다.

---

## Q: 운영 시 주의사항은?

A: 다음 세 가지를 배포 전 확인해야 한다.

1. **로드 밸런서 X-Forwarded-For 설정**: 리버스 프록시(Nginx, AWS ALB 등) 뒤에
   배포할 경우, 실제 클라이언트 IP가 `X-Forwarded-For` 헤더에 담겨야 한다.
   미들웨어에서 `request.client.host` 대신 해당 헤더를 우선 사용하도록 구성한다.

2. **제한값 튜닝**: 초기 배포 후 실제 트래픽 패턴을 2주 이상 관찰한 뒤
   `RATE_LIMIT_REQUESTS` 설정을 조정한다. 과도하게 낮은 제한은 정상 사용자를 차단한다.

3. **모니터링 알림 설정**: `429` 응답 비율이 전체 요청의 1% 이상이 되면
   알림을 발생시키도록 설정한다. 급증은 공격 또는 클라이언트 버그의 신호이다.
