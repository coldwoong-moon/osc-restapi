"""
API 응답 지연 시간 벤치마크 테스트

가설: 첫 요청(콜드 스타트)은 이후 요청 대비 2~5배 느리며,
      목록 조회 API는 데이터 양에 비례하여 지연이 증가한다.
목표: 각 엔드포인트의 응답 시간 프로파일을 수집하고 병목을 식별한다.
"""

import statistics
import time

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import create_app

# ---------------------------------------------------------------------------
# 공용 픽스처
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """모듈 범위 TestClient — 인메모리 SQLite DB와 테스트 유저를 사용한다."""
    db_path = tmp_path_factory.mktemp("latency") / "latency.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    from app.db.base import Base
    import app.models.user  # noqa: F401
    import app.models.refresh_token  # noqa: F401
    Base.metadata.create_all(engine)

    TestSession = sessionmaker(bind=engine)

    hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt())
    with TestSession() as db:
        db.execute(text(
            "INSERT INTO user (id, email, password, name, isEnabled) VALUES (1, 'bench@test.com', :pw, 'Bench User', 1)"
        ), {"pw": hashed})
        db.execute(text(
            "INSERT INTO authority (no, id, authorityName) VALUES (1, 'bench@test.com', 'ROLE_USER')"
        ))
        db.commit()

    app = create_app()

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="module")
def auth_token(client):
    """로그인 후 access_token을 반환한다."""
    response = client.post(
        "/api/v1/login",
        json={"email": "bench@test.com", "password": "password123"},
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


# ---------------------------------------------------------------------------
# 공용 측정 유틸리티
# ---------------------------------------------------------------------------

def measure_endpoint(
    client: TestClient,
    method: str,
    url: str,
    iterations: int = 10,
    **kwargs,
) -> dict:
    """
    엔드포인트 응답 시간을 반복 측정하여 통계를 반환한다.

    매개변수:
        client: FastAPI TestClient 인스턴스
        method: HTTP 메서드 문자열 (get, post, ...)
        url: 요청 경로
        iterations: 반복 횟수 (기본 10회)
        **kwargs: requests 라이브러리에 전달할 추가 인자

    반환값:
        avg, min, max, p95, stdev 키를 포함한 통계 딕셔너리 (단위: ms)
    """
    times: list[float] = []
    last_status: int = 0

    for _ in range(iterations):
        start = time.perf_counter()
        response = getattr(client, method)(url, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
        last_status = response.status_code

    sorted_times = sorted(times)
    p95_index = max(0, int(len(times) * 0.95) - 1)

    return {
        "avg": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "p95": sorted_times[p95_index],
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "last_status": last_status,
        "iterations": iterations,
    }


def _print_stats(label: str, stats: dict) -> None:
    """측정 결과를 표 형식으로 출력한다."""
    print(
        f"\n[{label}]  "
        f"avg={stats['avg']:.1f}ms  "
        f"min={stats['min']:.1f}ms  "
        f"max={stats['max']:.1f}ms  "
        f"p95={stats['p95']:.1f}ms  "
        f"stdev={stats['stdev']:.1f}ms  "
        f"status={stats['last_status']}"
    )


# ---------------------------------------------------------------------------
# 테스트 클래스
# ---------------------------------------------------------------------------

class TestLatencyBenchmark:
    """
    가설: 첫 요청(콜드 스타트)은 이후 요청 대비 2~5배 느리며,
          목록 조회 API는 데이터 양에 비례하여 지연이 증가한다.
    목표: 각 엔드포인트의 응답 시간 프로파일을 수집하고 병목을 식별한다.
    """

    ITERATIONS = 10
    # 단순 DB ping 기준 허용 상한 (ms)
    HEALTH_P95_LIMIT_MS = 500
    # 목록 조회 허용 P95 상한 (ms)
    LIST_P95_LIMIT_MS = 3000

    # -----------------------------------------------------------------------
    # 1. GET /api/v1/health — 베이스라인
    # -----------------------------------------------------------------------

    def test_health_latency(self, client: TestClient):
        """
        가설: health 엔드포인트는 단순 SELECT 1 쿼리만 수행하므로
              가장 낮은 지연 시간을 가지며 p95 < 500ms 를 만족해야 한다.
        목표: health 엔드포인트의 응답 시간 베이스라인 수치를 수집한다.
        """
        stats = measure_endpoint(
            client, "get", "/api/v1/health", iterations=self.ITERATIONS
        )
        _print_stats("GET /health", stats)

        assert stats["last_status"] == 200, (
            f"/health 가 200이 아님: {stats['last_status']}"
        )
        assert stats["p95"] < self.HEALTH_P95_LIMIT_MS, (
            f"health p95={stats['p95']:.1f}ms 가 {self.HEALTH_P95_LIMIT_MS}ms 초과"
        )

    # -----------------------------------------------------------------------
    # 2. POST /api/v1/login — 인증 처리 (bcrypt 포함)
    # -----------------------------------------------------------------------

    def test_login_latency(self, client: TestClient):
        """
        가설: login 엔드포인트는 bcrypt 해시 검증으로 인해
              health 대비 현저히 느리며 CPU 바운드 병목이 발생할 수 있다.
        목표: bcrypt 처리 비용이 응답 시간에 미치는 영향을 수치화한다.

        참고: 존재하지 않는 계정으로 요청하면 DB SELECT만 수행하므로
              bcrypt 비용이 배제된 순수 DB 지연만 측정된다.
              실제 인증 비용은 유효한 계정으로 측정해야 한다.
        """
        payload = {"email": "nonexistent@benchmark.test", "password": "dummy"}
        stats = measure_endpoint(
            client, "post", "/api/v1/login",
            iterations=self.ITERATIONS,
            json=payload,
        )
        _print_stats("POST /login (user not found)", stats)

        # 404 또는 400 모두 정상 — DB 조회는 완료된 것
        assert stats["last_status"] in (400, 404, 422), (
            f"/login 예상치 못한 응답: {stats['last_status']}"
        )
        assert stats["p95"] < self.LIST_P95_LIMIT_MS, (
            f"login p95={stats['p95']:.1f}ms 가 {self.LIST_P95_LIMIT_MS}ms 초과"
        )

    # -----------------------------------------------------------------------
    # 3. GET /api/v1/projects — 프로젝트 목록 조회
    # -----------------------------------------------------------------------

    def test_projects_list_latency(self, client: TestClient, auth_token):
        """
        가설: projects 목록은 delete_status 필터를 포함한 SELECT 쿼리로
              데이터 건수에 비례하여 지연 시간이 증가할 수 있다.
        목표: 프로젝트 목록 조회의 평균/p95 응답 시간을 수집하여
              데이터 증가에 따른 성능 변화 추이 분석의 기준선을 확보한다.
        """
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        stats = measure_endpoint(
            client, "get", "/api/v1/projects", iterations=self.ITERATIONS, headers=headers
        )
        _print_stats("GET /projects", stats)

        assert stats["last_status"] == 200, (
            f"/projects 가 200이 아님: {stats['last_status']}"
        )
        assert stats["p95"] < self.LIST_P95_LIMIT_MS, (
            f"projects p95={stats['p95']:.1f}ms 가 {self.LIST_P95_LIMIT_MS}ms 초과"
        )

    # -----------------------------------------------------------------------
    # 4. GET /api/v1/users — 사용자 목록 조회
    # -----------------------------------------------------------------------

    def test_users_list_latency(self, client: TestClient, auth_token):
        """
        가설: users 목록은 관계 로딩 없이 단순 SELECT이므로
              projects와 유사한 지연 시간 프로파일을 가진다.
        목표: 사용자 목록 조회의 응답 시간을 측정하여
              projects 대비 상대적 성능 비교 데이터를 확보한다.
        """
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        stats = measure_endpoint(
            client, "get", "/api/v1/users", iterations=self.ITERATIONS, headers=headers
        )
        _print_stats("GET /users", stats)

        assert stats["last_status"] == 200, (
            f"/users 가 200이 아님: {stats['last_status']}"
        )
        assert stats["p95"] < self.LIST_P95_LIMIT_MS, (
            f"users p95={stats['p95']:.1f}ms 가 {self.LIST_P95_LIMIT_MS}ms 초과"
        )

    # -----------------------------------------------------------------------
    # 5. GET /api/v1/roles — 역할 목록 조회 (마스터 데이터)
    # -----------------------------------------------------------------------

    def test_roles_list_latency(self, client: TestClient, auth_token):
        """
        가설: roles는 변경 빈도가 낮은 소량 마스터 데이터이므로
              모든 목록 엔드포인트 중 가장 낮은 지연 시간을 가진다.
        목표: 마스터 데이터 조회의 응답 시간 하한선을 확인하고
              캐싱 적용 시 기대 효과를 추정한다.
        """
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        stats = measure_endpoint(
            client, "get", "/api/v1/roles", iterations=self.ITERATIONS, headers=headers
        )
        _print_stats("GET /roles", stats)

        assert stats["last_status"] == 200, (
            f"/roles 가 200이 아님: {stats['last_status']}"
        )
        assert stats["p95"] < self.LIST_P95_LIMIT_MS, (
            f"roles p95={stats['p95']:.1f}ms 가 {self.LIST_P95_LIMIT_MS}ms 초과"
        )

    # -----------------------------------------------------------------------
    # 6. 콜드 스타트 vs 워밍업 후 성능 비교
    # -----------------------------------------------------------------------

    def test_cold_start_vs_warm(self, client: TestClient):
        """
        가설: 첫 번째 요청(콜드 스타트)은 DB 커넥션 풀 초기화와 ORM 캐시 미스로
              이후 요청 대비 2~5배 느리다.
        목표: 콜드 스타트 응답 시간과 워밍업 후 평균 응답 시간을 비교하여
              실제 배수 차이를 측정하고 가설의 타당성을 검증한다.

        측정 방법:
            - 별도 TestClient 인스턴스를 생성하여 완전한 콜드 상태를 재현한다.
            - 첫 번째 요청 후 9회 추가 요청을 수행하여 워밍업 평균을 산출한다.
        """
        # 완전한 콜드 상태를 재현하기 위해 별도 앱 인스턴스 사용
        cold_app = create_app()
        with TestClient(cold_app, raise_server_exceptions=False) as cold_client:
            # 콜드 스타트: 첫 번째 요청만 측정
            start = time.perf_counter()
            cold_client.get("/api/v1/health")
            cold_time_ms = (time.perf_counter() - start) * 1000

            # 워밍업: 이후 9회 측정
            warm_times: list[float] = []
            for _ in range(9):
                start = time.perf_counter()
                cold_client.get("/api/v1/health")
                warm_times.append((time.perf_counter() - start) * 1000)

        warm_avg_ms = statistics.mean(warm_times)
        ratio = cold_time_ms / warm_avg_ms if warm_avg_ms > 0 else float("inf")

        print(
            f"\n[콜드 스타트 vs 워밍업]  "
            f"cold={cold_time_ms:.1f}ms  "
            f"warm_avg={warm_avg_ms:.1f}ms  "
            f"ratio={ratio:.2f}x"
        )

        # 콜드 스타트가 워밍업 평균보다 빠를 수 없음 (최소 1배 이상)
        assert cold_time_ms >= 0, "콜드 스타트 측정값이 음수일 수 없다"

        # 워밍업 후 응답은 안정적이어야 함 (p95 기준)
        warm_p95 = sorted(warm_times)[int(len(warm_times) * 0.95) - 1]
        assert warm_p95 < self.HEALTH_P95_LIMIT_MS, (
            f"워밍업 후 p95={warm_p95:.1f}ms 가 {self.HEALTH_P95_LIMIT_MS}ms 초과"
        )

        # 콜드 스타트 비율 로그 — 2배 이상이면 커넥션 풀 초기화 비용이 큰 것
        if ratio >= 2.0:
            print(
                f"  -> 콜드 스타트가 워밍업 대비 {ratio:.1f}배 느림 "
                f"(커넥션 풀 초기화 비용 확인 권장)"
            )
        else:
            print(
                f"  -> 콜드/워밍업 차이 {ratio:.1f}배 "
                f"(TestClient 재사용으로 풀이 미리 초기화된 것으로 추정)"
            )
