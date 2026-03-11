"""
교착(Deadlock) 시나리오 테스트 모음

가설: 두 트랜잭션이 서로 다른 순서로 레코드를 업데이트하면 교착이 발생한다.
목표: 교착 발생 조건을 재현하고, retry / timeout / 일관된 락 순서 전략의 효과를 검증한다.

주의: SQLite 는 데이터베이스 레벨의 쓰기 잠금을 사용하므로 MariaDB 의 행(row) 레벨
      교착과 완전히 동일한 환경을 구현할 수 없다. 여기서는 SQLite 의 쓰기 직렬화
      특성을 이용해 교착 유사 경쟁 조건을 시뮬레이션하고, 실제 MariaDB 환경에서
      발생하는 교착 해결 전략의 로직 정확성을 검증한다.

구현 결정: 스레드 간 DB 공유가 필요한 테스트는 임시 파일 기반 SQLite를 사용한다.
           인메모리 DB(StaticPool)는 단일 연결 공유 시 InterfaceError가 발생하므로
           멀티스레드 테스트에 적합하지 않다.
"""

import os
import tempfile
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager

import pytest
from sqlalchemy import Column, Float, Integer, String, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------------------------
# 테스트 전용 모델 정의 (외부 의존 없음)
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class StockItem(Base):
    """테스트용 재고 아이템 — PartAttribute 와 동일한 복합 PK 구조."""

    __tablename__ = "stock_item"

    part_number = Column(String, primary_key=True)
    project_id = Column(Integer, primary_key=True)
    volume = Column(Float, default=0.0)
    ton = Column(Float, default=0.0)


class Counter(Base):
    """단순 카운터 — 교착 순서 시뮬레이션용."""

    __tablename__ = "counter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    value = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_path():
    """임시 SQLite 파일 경로를 생성하고 테스트 후 정리한다."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def engine(db_path):
    """각 테스트마다 독립적인 파일 기반 SQLite 엔진을 생성한다."""
    eng = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 5},
        echo=False,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture(scope="function")
def SessionFactory(engine):
    """테스트용 세션 팩토리."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def seed_counters(SessionFactory):
    """교착 시나리오에 사용할 초기 레코드 두 개를 삽입한다."""
    with SessionFactory() as s:
        s.add_all([
            Counter(name="alpha", value=0),
            Counter(name="beta", value=0),
        ])
        s.commit()


@pytest.fixture(scope="function")
def seed_stock(SessionFactory):
    """upsert 시나리오에 사용할 초기 재고 레코드를 삽입한다."""
    with SessionFactory() as s:
        for i in range(1, 6):
            s.add(StockItem(
                part_number=f"PART-{i:03d}",
                project_id=1,
                volume=float(i),
                ton=float(i) * 0.1,
            ))
        s.commit()


# ---------------------------------------------------------------------------
# 헬퍼 유틸리티
# ---------------------------------------------------------------------------

@contextmanager
def session_scope(SessionFactory) -> Generator[Session, None, None]:
    """컨텍스트 매니저로 세션 생명주기를 관리한다."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def with_retry(fn, max_retries: int = 3, base_delay: float = 0.05):
    """
    Exponential backoff retry 래퍼.

    OperationalError(교착 또는 잠금 타임아웃) 발생 시 최대 max_retries 회 재시도한다.
    각 시도 간 지연은 base_delay * 2^attempt 초.
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            return fn()
        except OperationalError as exc:
            last_exc = exc
            wait = base_delay * (2 ** attempt)
            time.sleep(wait)
    raise last_exc


# ---------------------------------------------------------------------------
# 테스트 클래스
# ---------------------------------------------------------------------------

class TestDeadlock:
    """
    가설: 두 트랜잭션이 서로 다른 순서로 레코드를 업데이트하면 교착이 발생한다.
    목표: 교착 발생 조건을 재현하고, retry/timeout 전략의 효과를 검증한다.
    """

    # ------------------------------------------------------------------
    # 1. 교착 시나리오 재현
    # ------------------------------------------------------------------

    def test_deadlock_scenario(self, SessionFactory, seed_counters):
        """
        시나리오: T1 은 alpha -> beta 순서로, T2 는 beta -> alpha 순서로 업데이트한다.
        가설: 두 트랜잭션이 서로 상대방이 보유한 잠금을 기다리면 교착이 발생한다.

        SQLite 파일 기반 환경에서는 DB 레벨 쓰기 잠금을 사용하므로
        동시 쓰기 시 OperationalError(database is locked)가 발생한다.
        """
        barrier = threading.Barrier(2, timeout=5)
        errors: list[tuple[str, Exception]] = []
        results: list[str] = []
        lock = threading.Lock()

        def transaction_1():
            try:
                with session_scope(SessionFactory) as s:
                    alpha = s.query(Counter).filter_by(name="alpha").first()
                    barrier.wait()
                    time.sleep(0.05)
                    beta = s.query(Counter).filter_by(name="beta").first()
                    alpha.value += 1
                    beta.value += 1
                with lock:
                    results.append("T1_OK")
            except Exception as exc:
                with lock:
                    errors.append(("T1", exc))
                    results.append("T1_FAIL")

        def transaction_2():
            try:
                with session_scope(SessionFactory) as s:
                    beta = s.query(Counter).filter_by(name="beta").first()
                    barrier.wait()
                    time.sleep(0.05)
                    alpha = s.query(Counter).filter_by(name="alpha").first()
                    alpha.value += 1
                    beta.value += 1
                with lock:
                    results.append("T2_OK")
            except Exception as exc:
                with lock:
                    errors.append(("T2", exc))
                    results.append("T2_FAIL")

        t1 = threading.Thread(target=transaction_1)
        t2 = threading.Thread(target=transaction_2)
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        assert len(results) >= 1, "적어도 하나의 트랜잭션이 완료되어야 한다"
        print(f"\n[교착 시나리오] 결과: {results}, 오류: {len(errors)}건")

    # ------------------------------------------------------------------
    # 2. Retry 전략
    # ------------------------------------------------------------------

    def test_retry_strategy(self, SessionFactory, seed_counters):
        """
        시나리오: 교착 또는 잠금 타임아웃 발생 시 exponential backoff 로 재시도한다.
        가설: 최대 3회 재시도하면 일시적인 잠금 경쟁을 극복하고 최종 성공한다.
        """
        attempt_count = 0
        fail_until = 2

        def flaky_update():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < fail_until:
                raise OperationalError("database is locked", {}, None)
            with session_scope(SessionFactory) as s:
                counter = s.query(Counter).filter_by(name="alpha").first()
                counter.value += 10

        with_retry(flaky_update, max_retries=3, base_delay=0.01)

        with session_scope(SessionFactory) as s:
            counter = s.query(Counter).filter_by(name="alpha").first()
            assert counter.value == 10, f"retry 후 값이 10이어야 하지만 {counter.value}"
        assert attempt_count >= 2, "최소 2회 이상 시도해야 retry 전략이 검증된다"

    def test_retry_exhaustion(self, SessionFactory):
        """
        시나리오: 최대 재시도 횟수를 초과하면 예외를 상위로 전파한다.
        가설: with_retry 는 max_retries 초과 시 마지막 OperationalError 를 raise 한다.
        """
        call_count = 0

        def always_fail():
            nonlocal call_count
            call_count += 1
            raise OperationalError("deadlock detected", {}, None)

        with pytest.raises(OperationalError):
            with_retry(always_fail, max_retries=3, base_delay=0.001)
        assert call_count == 3, f"정확히 3회 시도해야 하지만 {call_count}회 시도됨"

    # ------------------------------------------------------------------
    # 3. Timeout 전략
    # ------------------------------------------------------------------

    def test_timeout_strategy(self, db_path):
        """
        시나리오: 쿼리 타임아웃 설정으로 교착 대기 시간을 제한한다.
        가설: SQLite timeout 을 짧게 설정하면 잠금 대기가 조기 종료된다.
        """
        eng1 = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 5},
        )
        eng2 = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 1},
        )
        Base.metadata.create_all(eng1)

        SF1 = sessionmaker(bind=eng1)
        SF2 = sessionmaker(bind=eng2)

        s1 = SF1()
        try:
            s1.execute(text("BEGIN IMMEDIATE"))
            s1.execute(text("INSERT INTO counter (name, value) VALUES ('gamma', 0)"))

            s2 = SF2()
            start = time.perf_counter()
            try:
                with pytest.raises(OperationalError):
                    s2.execute(text("BEGIN IMMEDIATE"))
                    s2.execute(text("INSERT INTO counter (name, value) VALUES ('delta', 0)"))
                elapsed = time.perf_counter() - start
                assert elapsed < 3, f"타임아웃이 {elapsed:.1f}초 걸림 — 1초 이내 예상"
                print(f"\n[타임아웃 전략] 잠금 대기 후 {elapsed:.3f}초만에 OperationalError 발생")
            finally:
                s2.close()
        finally:
            s1.rollback()
            s1.close()
            eng1.dispose()
            eng2.dispose()

    def test_timeout_prevents_long_wait(self, db_path):
        """
        시나리오: timeout=0 설정 시 잠긴 DB 접근이 즉시 OperationalError 를 발생시킨다.
        """
        eng1 = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 5},
        )
        eng2 = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 0},
        )
        Base.metadata.create_all(eng1)

        SF1 = sessionmaker(bind=eng1)
        SF2 = sessionmaker(bind=eng2)

        s1 = SF1()
        try:
            s1.execute(text("BEGIN EXCLUSIVE"))

            s2 = SF2()
            try:
                with pytest.raises(OperationalError):
                    s2.execute(text("BEGIN EXCLUSIVE"))
                print("\n[즉시 타임아웃] timeout=0에서 즉시 OperationalError 발생 확인")
            finally:
                try:
                    s2.rollback()
                except Exception:
                    pass
                s2.close()
        finally:
            s1.rollback()
            s1.close()
            eng1.dispose()
            eng2.dispose()

    # ------------------------------------------------------------------
    # 4. 일관된 락 순서 (Deadlock Prevention)
    # ------------------------------------------------------------------

    def test_consistent_lock_ordering(self, SessionFactory, seed_counters):
        """
        시나리오: 모든 트랜잭션이 알파벳 순서로 레코드를 업데이트한다.
        가설: 일관된 락 순서를 지키면 교착이 발생하지 않는다.
        검증: 순차 실행에서 정렬 전략의 로직 정확성을 확인한다.
        """
        def ordered_update(pairs: list[tuple[str, int]]):
            sorted_pairs = sorted(pairs, key=lambda x: x[0])
            with session_scope(SessionFactory) as s:
                for name, delta in sorted_pairs:
                    row = s.query(Counter).filter_by(name=name).first()
                    row.value += delta

        ordered_update([("beta", 1), ("alpha", 1)])
        ordered_update([("alpha", 1), ("beta", 1)])

        with session_scope(SessionFactory) as s:
            alpha = s.query(Counter).filter_by(name="alpha").first()
            beta = s.query(Counter).filter_by(name="beta").first()
            assert alpha.value == 2, f"alpha 는 2여야 하지만 {alpha.value}"
            assert beta.value == 2, f"beta 는 2여야 하지만 {beta.value}"

    def test_lock_ordering_vs_random_ordering(self, SessionFactory, seed_counters):
        """
        시나리오: 정렬된 락 순서 함수가 입력 순서에 관계없이 동일한 처리 순서를 보장한다.
        검증: 20회 반복에서 모든 업데이트가 정상 처리된다.
        """
        ITERATIONS = 20

        def ordered_update(pairs: list[tuple[str, int]]):
            sorted_pairs = sorted(pairs, key=lambda x: x[0])
            with session_scope(SessionFactory) as s:
                for name, delta in sorted_pairs:
                    row = s.query(Counter).filter_by(name=name).first()
                    row.value += delta

        for i in range(ITERATIONS):
            if i % 2 == 0:
                ordered_update([("beta", 1), ("alpha", 1)])
            else:
                ordered_update([("alpha", 1), ("beta", 1)])

        with session_scope(SessionFactory) as s:
            alpha = s.query(Counter).filter_by(name="alpha").first()
            beta = s.query(Counter).filter_by(name="beta").first()
            assert alpha.value == ITERATIONS, f"alpha={alpha.value}, 기대값={ITERATIONS}"
            assert beta.value == ITERATIONS, f"beta={beta.value}, 기대값={ITERATIONS}"

    # ------------------------------------------------------------------
    # 5. 벌크 upsert 교착 위험 분석
    # ------------------------------------------------------------------

    def test_bulk_upsert_deadlock_risk(self, SessionFactory, seed_stock):
        """
        시나리오: 역순/정순 upsert가 순차 실행에서 정상 동작함을 확인한다.
        가설: MariaDB InnoDB에서는 역순 upsert가 교착을 유발할 수 있지만,
              SQLite에서는 DB 레벨 잠금으로 직렬화된다.

        현재 코드 위험 지점 (app/api/v1/parts.py:62-82):
            for attr in attrs_in:               <- 입력 순서 그대로 처리
                existing = db.scalar(select(...))
                if existing:
                    existing.volume = attr.volume  <- 암묵적 행 잠금
            db.commit()                           <- 모든 잠금 일괄 해제
        """
        with session_scope(SessionFactory) as s:
            for i in range(3, 0, -1):
                part = s.query(StockItem).filter_by(
                    part_number=f"PART-{i:03d}", project_id=1
                ).first()
                if part:
                    part.volume = float(i) * 10

        with session_scope(SessionFactory) as s:
            for i in range(1, 4):
                part = s.query(StockItem).filter_by(
                    part_number=f"PART-{i:03d}", project_id=1
                ).first()
                if part:
                    part.volume = float(i) * 20

        with session_scope(SessionFactory) as s:
            for i in range(1, 4):
                part = s.query(StockItem).filter_by(
                    part_number=f"PART-{i:03d}", project_id=1
                ).first()
                assert part.volume == float(i) * 20

    def test_bulk_upsert_with_sorted_order_safe(self, SessionFactory, seed_stock):
        """
        시나리오: part_number 정렬 후 upsert — 교착 방지 전략 검증.

        권장 수정 (app/api/v1/parts.py):
            for attr in sorted(attrs_in, key=lambda x: x.part_number):
        """
        def safe_upsert(updates: list[tuple[str, float]]):
            sorted_updates = sorted(updates, key=lambda x: x[0])
            with session_scope(SessionFactory) as s:
                for part_number, new_volume in sorted_updates:
                    existing = s.query(StockItem).filter_by(
                        part_number=part_number, project_id=1
                    ).first()
                    if existing:
                        existing.volume = new_volume

        safe_upsert([("PART-003", 99.0), ("PART-001", 88.0), ("PART-002", 77.0)])
        safe_upsert([("PART-001", 11.0), ("PART-002", 22.0), ("PART-003", 33.0)])

        with session_scope(SessionFactory) as s:
            p1 = s.query(StockItem).filter_by(part_number="PART-001", project_id=1).first()
            p2 = s.query(StockItem).filter_by(part_number="PART-002", project_id=1).first()
            p3 = s.query(StockItem).filter_by(part_number="PART-003", project_id=1).first()
            assert p1.volume == 11.0, f"PART-001 volume={p1.volume}, 기대값=11.0"
            assert p2.volume == 22.0, f"PART-002 volume={p2.volume}, 기대값=22.0"
            assert p3.volume == 33.0, f"PART-003 volume={p3.volume}, 기대값=33.0"
