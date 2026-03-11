"""
DB 커넥션 풀 고갈 가설 검증 테스트

가설: 동시 사용자 수가 pool_size를 초과하면 응답 지연이 급격히 증가하고,
     max_overflow를 초과하면 QueuePool overflow 에러가 발생한다.

목표: pool_size 설정(5 / 20 / 50)별 동시 요청 처리 성능을 수치로 비교하여
     최적 설정 권장값을 도출한다.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import pytest


# ---------------------------------------------------------------------------
# 헬퍼: Mock 엔진 팩토리
# ---------------------------------------------------------------------------

def _make_mock_engine(pool_size: int, max_overflow: int, checkout_delay: float = 0.05):
    """
    실제 DB 없이 SQLAlchemy QueuePool 동작을 시뮬레이션하는 엔진을 생성한다.

    핵심 동작:
    - 동시 활성 커넥션 수(concurrent_active)를 원자적으로 추적한다.
    - connect() 호출 시점에 pool_size + max_overflow를 초과하면 즉시 OperationalError를 발생시킨다.
    - 이는 실제 QueuePool의 pool_timeout=0 (즉시 실패) 동작을 모델링한다.
    - checkout_delay: 커넥션 체크아웃 시 소요되는 모의 시간(초).
    """
    capacity = pool_size + max_overflow
    lock = threading.Lock()
    concurrent_active = [0]   # 현재 동시 활성 커넥션 수
    peak_active = [0]         # 피크 동시 활성 수

    class _FakeConn:
        """풀에서 체크아웃된 가짜 커넥션."""

        def __init__(self):
            time.sleep(checkout_delay)  # 커넥션 획득 지연 시뮬레이션
            self._closed = False

        def execute(self, stmt):
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [{"1": 1}]
            return mock_result

        def close(self):
            if not self._closed:
                self._closed = True
                with lock:
                    concurrent_active[0] -= 1

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    class _FakeEngine:
        def connect(self):
            # 원자적으로 활성 수를 확인하고 증가
            with lock:
                if concurrent_active[0] >= capacity:
                    raise OperationalError(
                        "QueuePool limit of size %d overflow %d reached, "
                        "connection timed out, timeout 0" % (pool_size, max_overflow),
                        None,
                        None,
                    )
                concurrent_active[0] += 1
                if concurrent_active[0] > peak_active[0]:
                    peak_active[0] = concurrent_active[0]
            return _FakeConn()

        @property
        def peak_concurrent(self):
            return peak_active[0]

    return _FakeEngine()


def _run_concurrent_requests(engine, num_sessions: int, work_duration: float = 0.1):
    """
    num_sessions 개의 동시 요청을 ThreadPoolExecutor로 실행하고
    각 요청의 소요 시간 및 에러 여부를 반환한다.

    반환값: (results, errors)
      results: 성공한 요청의 소요 시간 리스트(초)
      errors:  실패한 요청의 예외 문자열 리스트
    """
    results = []
    errors = []
    results_lock = threading.Lock()

    def _single_request(_):
        t0 = time.perf_counter()
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                time.sleep(work_duration)  # 실제 쿼리 실행 시간 시뮬레이션
            elapsed = time.perf_counter() - t0
            with results_lock:
                results.append(elapsed)
        except OperationalError as exc:
            with results_lock:
                errors.append(str(exc))

    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(_single_request, i) for i in range(num_sessions)]
        for f in as_completed(futures):
            f.result()  # 내부에서 수집 완료 — 재전파 없음

    return results, errors


# ---------------------------------------------------------------------------
# 테스트 클래스
# ---------------------------------------------------------------------------

class TestConnectionPool:
    """
    가설: 동시 사용자가 pool_size를 초과하면 응답 지연이 급격히 증가한다.
    목표: pool_size 설정별 동시 요청 처리 성능을 수치로 비교한다.
    """

    # -----------------------------------------------------------------------
    # 1. 동시 10세션 — 소형 풀(pool_size=5)에서의 기본 부하
    # -----------------------------------------------------------------------

    def test_concurrent_10_sessions(self):
        """
        가설: pool_size=5, max_overflow=5인 환경에서 동시 10 세션 요청은
             풀 용량(10)과 정확히 일치하므로 전원 성공한다.
        목표: 10개 요청 전원 성공, 에러 0건, 평균 응답 시간 < 1.0초 확인.
        """
        engine = _make_mock_engine(pool_size=5, max_overflow=5, checkout_delay=0.02)
        results, errors = _run_concurrent_requests(engine, num_sessions=10, work_duration=0.05)

        assert len(errors) == 0, f"예상치 못한 에러 발생: {errors}"
        assert len(results) == 10, "10개 요청이 모두 완료되어야 한다"

        avg_time = sum(results) / len(results)
        max_time = max(results)

        print(f"\n[10 sessions / pool_size=5] avg={avg_time:.3f}s  max={max_time:.3f}s")
        assert avg_time < 1.0, f"평균 응답 시간 초과: {avg_time:.3f}s"

    # -----------------------------------------------------------------------
    # 2. 동시 50세션 — 소형 풀(pool_size=5, max_overflow=5) 고갈 검증
    # -----------------------------------------------------------------------

    def test_concurrent_50_sessions(self):
        """
        가설: pool_size=5, max_overflow=5 환경에서 동시 50 세션 요청 시
             용량(10)을 초과하는 40건이 OperationalError로 실패한다.
        목표: 에러 발생 확인, 성공 수 <= 용량(10), 에러 메시지에 'QueuePool limit' 포함.
        """
        POOL_SIZE = 5
        MAX_OVERFLOW = 5
        CAPACITY = POOL_SIZE + MAX_OVERFLOW  # 10

        engine = _make_mock_engine(
            pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, checkout_delay=0.02
        )
        results, errors = _run_concurrent_requests(engine, num_sessions=50, work_duration=0.2)

        total = len(results) + len(errors)
        assert total == 50, "전체 요청 수가 50이어야 한다"

        # 용량(10) 초과 요청은 overflow 에러 발생 필수
        assert len(errors) > 0, (
            "소형 풀(pool_size=5, max_overflow=5)에서 50 동시 요청 시 "
            "overflow 에러가 반드시 발생해야 한다"
        )
        assert len(results) <= CAPACITY, (
            f"성공 요청({len(results)})이 풀 용량({CAPACITY})을 초과할 수 없다"
        )

        success_rate = len(results) / total * 100
        print(
            f"\n[50 sessions / pool_size=5] "
            f"success={len(results)} ({success_rate:.1f}%)  "
            f"errors={len(errors)}  capacity={CAPACITY}"
        )

    # -----------------------------------------------------------------------
    # 3. 동시 100세션 — 대형 풀(pool_size=50)의 수용 한계 검증
    # -----------------------------------------------------------------------

    def test_concurrent_100_sessions(self):
        """
        가설: pool_size=50, max_overflow=50 환경에서는 동시 100 세션도
             전부 수용되어 에러가 발생하지 않는다.
        목표: 100개 요청 전원 성공, 에러 0건, 평균 응답 시간 < 2.0초 확인.
        """
        engine = _make_mock_engine(pool_size=50, max_overflow=50, checkout_delay=0.02)
        results, errors = _run_concurrent_requests(engine, num_sessions=100, work_duration=0.05)

        assert len(errors) == 0, f"대형 풀에서 100 세션 실패: {errors[:3]}"
        assert len(results) == 100

        avg_time = sum(results) / len(results)
        max_time = max(results)

        print(
            f"\n[100 sessions / pool_size=50] "
            f"avg={avg_time:.3f}s  max={max_time:.3f}s"
        )
        assert avg_time < 2.0, f"평균 응답 시간 초과: {avg_time:.3f}s"

    # -----------------------------------------------------------------------
    # 4. pool_size 설정별 성능 비교 (5 / 20 / 50)
    # -----------------------------------------------------------------------

    def test_pool_size_comparison(self):
        """
        가설: pool_size가 클수록 동시 요청 처리 성공률이 높아진다.
        목표: pool_size=5 / 20 / 50 각각에서 30 동시 요청을 처리하고
             성공률과 에러 수를 비교하여 상관관계를 검증한다.

        설정:
          - pool_size=5,  max_overflow=5  → 용량=10  → 30 요청 중 20건 실패 예상
          - pool_size=20, max_overflow=10 → 용량=30  → 30 요청 전원 성공 예상
          - pool_size=50, max_overflow=10 → 용량=60  → 30 요청 전원 성공 예상
        """
        configs = [
            {"pool_size": 5,  "max_overflow": 5,  "expected_errors": True},
            {"pool_size": 20, "max_overflow": 10, "expected_errors": False},
            {"pool_size": 50, "max_overflow": 10, "expected_errors": False},
        ]
        NUM_SESSIONS = 30
        summary = []

        for cfg in configs:
            engine = _make_mock_engine(
                pool_size=cfg["pool_size"],
                max_overflow=cfg["max_overflow"],
                checkout_delay=0.02,
            )
            results, errors = _run_concurrent_requests(
                engine, num_sessions=NUM_SESSIONS, work_duration=0.2
            )
            capacity = cfg["pool_size"] + cfg["max_overflow"]
            success_rate = len(results) / NUM_SESSIONS * 100
            avg_time = sum(results) / len(results) if results else float("inf")
            summary.append(
                {
                    "pool_size": cfg["pool_size"],
                    "capacity": capacity,
                    "success_rate": success_rate,
                    "avg_time": avg_time,
                    "errors": len(errors),
                    "expected_errors": cfg["expected_errors"],
                }
            )

        print("\n[pool_size 비교 -- 30 동시 요청]")
        print(f"{'pool_size':>10} {'용량':>6} {'성공률(%)':>10} {'avg(s)':>8} {'에러':>6}")
        for row in summary:
            print(
                f"{row['pool_size']:>10} "
                f"{row['capacity']:>6} "
                f"{row['success_rate']:>10.1f} "
                f"{row['avg_time']:>8.3f} "
                f"{row['errors']:>6}"
            )

        # pool_size=5 (용량=10): 30 세션 중 20건 실패 예상
        assert summary[0]["errors"] > 0, (
            "pool_size=5(용량=10)에서 30 동시 요청 시 에러가 없으면 가설 재검토 필요"
        )
        assert summary[0]["success_rate"] < 100.0, (
            "pool_size=5에서 성공률이 100%이면 overflow가 발생하지 않은 것"
        )

        # pool_size=20 (용량=30): 30 세션 전원 성공
        assert summary[1]["errors"] == 0, (
            f"pool_size=20(용량=30)에서 30 요청이 전원 성공해야 한다. "
            f"실패: {summary[1]['errors']}건"
        )

        # pool_size=50 (용량=60): 30 세션 전원 성공
        assert summary[2]["errors"] == 0, (
            f"pool_size=50(용량=60)에서는 30 요청이 전원 성공해야 한다. "
            f"실패: {summary[2]['errors']}건"
        )

        # pool_size 증가 → 성공률 단조 비감소
        assert summary[0]["success_rate"] <= summary[1]["success_rate"], (
            "pool_size 5 → 20 증가 시 성공률이 같거나 증가해야 한다"
        )
        assert summary[1]["success_rate"] <= summary[2]["success_rate"], (
            "pool_size 20 → 50 증가 시 성공률이 같거나 증가해야 한다"
        )

    # -----------------------------------------------------------------------
    # 5. 커넥션 풀 고갈 시 QueuePool overflow 에러 시뮬레이션
    # -----------------------------------------------------------------------

    def test_pool_overflow_behavior(self):
        """
        가설: pool_size + max_overflow를 초과하는 동시 요청은
             SQLAlchemy QueuePool이 즉시 OperationalError를 발생시킨다.
        목표:
          - overflow 에러 발생 확인
          - 에러 메시지에 'QueuePool limit' 문자열 포함
          - 성공 요청 수 <= pool_size + max_overflow (풀 용량)
        """
        POOL_SIZE = 3
        MAX_OVERFLOW = 2
        CAPACITY = POOL_SIZE + MAX_OVERFLOW  # 5
        NUM_SESSIONS = 20  # 용량(5)의 4배 — 명확한 overflow 유발

        engine = _make_mock_engine(
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            checkout_delay=0.01,
        )
        results, errors = _run_concurrent_requests(
            engine, num_sessions=NUM_SESSIONS, work_duration=0.3
        )

        # overflow 에러가 반드시 발생해야 함
        assert len(errors) > 0, "pool 용량 초과 시 OperationalError가 발생해야 한다"

        # 에러 메시지 검증
        for err_msg in errors:
            assert "QueuePool limit" in err_msg, (
                f"에러 메시지에 'QueuePool limit'이 없음: {err_msg}"
            )

        # 성공한 요청은 최대 CAPACITY 이하여야 함
        assert len(results) <= CAPACITY, (
            f"성공 요청({len(results)})이 풀 용량({CAPACITY})을 초과할 수 없다"
        )

        # 총 요청 수 보존
        assert len(results) + len(errors) == NUM_SESSIONS

        print(
            f"\n[overflow 시뮬레이션] "
            f"capacity={CAPACITY}  "
            f"success={len(results)}  "
            f"overflow_errors={len(errors)}"
        )
        print(f"  에러 샘플: {errors[0][:80]}")
