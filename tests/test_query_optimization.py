"""
N+1 쿼리 문제 감지 및 최적화 테스트

이 모듈은 현재 CRUDBase 패턴에서 relationship 접근 시 발생하는
N+1 쿼리 문제를 정량적으로 식별하고, eager loading 적용 후
쿼리 수가 실질적으로 감소함을 검증한다.

실행 방법:
    pytest tests/test_query_optimization.py -v
"""

import pytest
from sqlalchemy import Column, ForeignKey, Integer, String, event, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    joinedload,
    relationship,
    selectinload,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------------------------------
# 테스트 전용 인메모리 Base (프로덕션 Base와 분리)
# ---------------------------------------------------------------------------

class _Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# 테스트 전용 모델 (실제 모델 구조를 반영)
# ---------------------------------------------------------------------------

class TProject(_Base):
    """Project -> ProjectModel (1:N) 관계를 재현한 테스트 모델"""
    __tablename__ = "t_project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))

    models = relationship("TProjectModel", back_populates="project", lazy="select")


class TProjectModel(_Base):
    """ProjectModel 테스트 모델"""
    __tablename__ = "t_project_model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    project_id = Column(Integer, ForeignKey("t_project.id"))

    project = relationship("TProject", back_populates="models", lazy="select")


class TPartner(_Base):
    """Partner 테스트 모델"""
    __tablename__ = "t_partner"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))


class TUser(_Base):
    """User -> Partner (N:1) 관계를 재현한 테스트 모델"""
    __tablename__ = "t_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    partner_id = Column(Integer, ForeignKey("t_partner.id"), nullable=True)

    partner = relationship("TPartner", foreign_keys=[partner_id], lazy="select")


class TCarryInRequest(_Base):
    """CarryInRequest -> CarryInRequestItem (1:N) 관계를 재현한 테스트 모델"""
    __tablename__ = "t_carry_in_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))

    items = relationship("TCarryInRequestItem", back_populates="carry_in_request", lazy="select")


class TCarryInRequestItem(_Base):
    """CarryInRequestItem 테스트 모델"""
    __tablename__ = "t_carry_in_request_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carry_in_request_id = Column(Integer, ForeignKey("t_carry_in_request.id"))
    part_number = Column(String(100))
    quantity = Column(Integer)

    carry_in_request = relationship("TCarryInRequest", back_populates="items", lazy="select")


# ---------------------------------------------------------------------------
# 쿼리 카운터 헬퍼
# ---------------------------------------------------------------------------

class QueryCounter:
    """SQL 쿼리 실행 횟수를 카운트하는 헬퍼.

    SQLAlchemy event listener를 활용해 engine 레벨에서
    실제 DB로 전송되는 SQL 문 수를 추적한다.
    """

    def __init__(self, engine):
        self.count = 0
        self._engine = engine
        event.listen(engine, "before_cursor_execute", self._callback)

    def _callback(self, conn, cursor, statement, parameters, context, executemany):
        """before_cursor_execute 이벤트 콜백 - SQL 실행마다 카운트 증가"""
        self.count += 1

    def reset(self):
        """카운트를 0으로 초기화"""
        self.count = 0

    def remove(self):
        """이벤트 리스너 제거 (테스트 격리)"""
        event.remove(self._engine, "before_cursor_execute", self._callback)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def engine():
    """모듈 범위 SQLite 인메모리 엔진 생성"""
    _engine = create_engine("sqlite:///:memory:", echo=False)
    _Base.metadata.create_all(_engine)
    yield _engine
    _Base.metadata.drop_all(_engine)
    _engine.dispose()


@pytest.fixture(scope="module")
def seed_data(engine):
    """테스트용 시드 데이터 삽입 (모듈 범위 1회 실행)"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        # Partner 3개
        partners = [TPartner(name=f"파트너_{i}") for i in range(1, 4)]
        db.add_all(partners)
        db.flush()

        # User 5명 (파트너 연결)
        users = [
            TUser(name=f"사용자_{i}", partner_id=partners[i % 3].id)
            for i in range(5)
        ]
        db.add_all(users)

        # Project 5개, 각각 ProjectModel 3개
        for pi in range(1, 6):
            project = TProject(name=f"프로젝트_{pi}")
            db.add(project)
            db.flush()
            for mi in range(1, 4):
                db.add(TProjectModel(name=f"모델_{pi}_{mi}", project_id=project.id))

        # CarryInRequest 4개, 각각 item 3개
        for ri in range(1, 5):
            req = TCarryInRequest(title=f"반입요청_{ri}")
            db.add(req)
            db.flush()
            for ii in range(1, 4):
                db.add(TCarryInRequestItem(
                    carry_in_request_id=req.id,
                    part_number=f"PART-{ri}-{ii:03d}",
                    quantity=ii * 10,
                ))

        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 테스트 클래스
# ---------------------------------------------------------------------------

class TestQueryOptimization:
    """
    가설: 현재 CRUDBase.get_multi() 패턴(lazy="select")은
          relationship 접근 시 N+1 쿼리가 발생한다.
    목표: N+1 발생 지점을 정량적으로 식별하고,
          eager loading 적용 후 쿼리 수가 1~2회로 줄어듦을 검증한다.
    """

    def test_n_plus_1_detection_project_models(self, engine, seed_data):
        """Project 목록 조회 후 각 Project.models 접근 시 N+1 쿼리가 발생한다.

        - 5개의 Project를 SELECT (1회)
        - 각 Project.models 접근마다 별도 SELECT 발생 (5회)
        - 총 6회 이상의 쿼리가 실행되어 N+1 문제임을 확인
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            # CRUDBase.get_multi() 와 동일한 단순 쿼리 패턴
            projects = list(db.scalars(select(TProject)).all())
            query_after_list = counter.count  # 목록 조회 쿼리 수

            # relationship 접근 - lazy loading으로 N번 추가 쿼리 발생
            all_model_names = []
            for proj in projects:
                all_model_names.extend([m.name for m in proj.models])

            total_queries = counter.count
            n_plus_1_queries = total_queries - query_after_list

            assert len(projects) == 5, "프로젝트 5개가 조회되어야 한다"
            assert len(all_model_names) == 15, "총 15개의 모델 이름이 수집되어야 한다"

            # N+1: 5개 프로젝트 각각에 대해 models SELECT가 발생해야 한다
            assert n_plus_1_queries == 5, (
                f"N+1 쿼리 5회가 발생해야 하는데 {n_plus_1_queries}회 발생함"
            )
            assert total_queries >= 6, (
                f"총 쿼리가 6회 이상이어야 하는데 {total_queries}회임"
            )
        finally:
            counter.remove()
            db.close()

    def test_n_plus_1_detection_carry_in_items(self, engine, seed_data):
        """CarryInRequest 목록 조회 후 각 request.items 접근 시 N+1 쿼리가 발생한다.

        - 4개의 CarryInRequest를 SELECT (1회)
        - 각 request.items 접근마다 별도 SELECT 발생 (4회)
        - 총 5회 이상의 쿼리가 실행되어 N+1 문제임을 확인
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            requests = list(db.scalars(select(TCarryInRequest)).all())
            query_after_list = counter.count

            all_part_numbers = []
            for req in requests:
                all_part_numbers.extend([item.part_number for item in req.items])

            total_queries = counter.count
            n_plus_1_queries = total_queries - query_after_list

            assert len(requests) == 4, "반입요청 4개가 조회되어야 한다"
            assert len(all_part_numbers) == 12, "총 12개의 part_number가 수집되어야 한다"
            assert n_plus_1_queries == 4, (
                f"N+1 쿼리 4회가 발생해야 하는데 {n_plus_1_queries}회 발생함"
            )
        finally:
            counter.remove()
            db.close()

    def test_n_plus_1_detection_user_partner(self, engine, seed_data):
        """User 목록 조회 후 각 user.partner 접근 시 N+1 쿼리가 발생한다.

        - 5명의 User를 SELECT (1회)
        - 각 user.partner 접근마다 별도 SELECT 발생 (최대 5회, 캐시 없을 때)
        - 총 2회 이상의 쿼리가 실행됨을 확인
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            users = list(db.scalars(select(TUser)).all())
            query_after_list = counter.count

            partner_names = []
            for user in users:
                if user.partner:
                    partner_names.append(user.partner.name)

            total_queries = counter.count
            n_plus_1_queries = total_queries - query_after_list

            assert len(users) == 5, "사용자 5명이 조회되어야 한다"
            # SQLAlchemy identity map이 일부 캐시할 수 있으나
            # 처음 접근 시에는 반드시 추가 쿼리 발생
            assert n_plus_1_queries >= 1, (
                f"Partner lazy loading으로 추가 쿼리가 발생해야 하는데 {n_plus_1_queries}회임"
            )
        finally:
            counter.remove()
            db.close()

    def test_joinedload_optimization_project_models(self, engine, seed_data):
        """joinedload 적용 시 Project + models를 단 1회 JOIN 쿼리로 조회한다.

        - joinedload(TProject.models) 옵션으로 JOIN SELECT 1회 실행
        - relationship 접근 시 추가 쿼리 0회
        - 총 1회 쿼리로 N+1 문제가 해결됨을 검증
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            # eager loading 적용
            stmt = select(TProject).options(joinedload(TProject.models))
            projects = list(db.scalars(stmt.distinct()).unique().all())
            query_after_list = counter.count

            # relationship 접근 - 이미 로드되어 있으므로 추가 쿼리 없음
            all_model_names = []
            for proj in projects:
                all_model_names.extend([m.name for m in proj.models])

            total_queries = counter.count
            extra_queries = total_queries - query_after_list

            assert len(projects) == 5, "프로젝트 5개가 조회되어야 한다"
            assert len(all_model_names) == 15, "총 15개의 모델 이름이 수집되어야 한다"
            assert query_after_list == 1, (
                f"joinedload는 1회 쿼리로 조회해야 하는데 {query_after_list}회 실행됨"
            )
            assert extra_queries == 0, (
                f"relationship 접근 시 추가 쿼리가 0이어야 하는데 {extra_queries}회 발생함"
            )
        finally:
            counter.remove()
            db.close()

    def test_selectinload_optimization_carry_in_items(self, engine, seed_data):
        """selectinload 적용 시 CarryInRequest + items를 2회 쿼리로 조회한다.

        - SELECT carry_in_request (1회)
        - SELECT carry_in_request_item WHERE id IN (...) (1회)
        - relationship 접근 시 추가 쿼리 0회
        - 총 2회 쿼리로 N+1 문제 해결
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            stmt = select(TCarryInRequest).options(
                selectinload(TCarryInRequest.items)
            )
            requests = list(db.scalars(stmt).all())
            query_after_list = counter.count

            all_part_numbers = []
            for req in requests:
                all_part_numbers.extend([item.part_number for item in req.items])

            total_queries = counter.count
            extra_queries = total_queries - query_after_list

            assert len(requests) == 4, "반입요청 4개가 조회되어야 한다"
            assert len(all_part_numbers) == 12, "총 12개의 part_number가 수집되어야 한다"
            assert query_after_list == 2, (
                f"selectinload는 2회 쿼리로 조회해야 하는데 {query_after_list}회 실행됨"
            )
            assert extra_queries == 0, (
                f"relationship 접근 시 추가 쿼리가 0이어야 하는데 {extra_queries}회 발생함"
            )
        finally:
            counter.remove()
            db.close()

    def test_selectinload_optimization_user_partner(self, engine, seed_data):
        """selectinload 적용 시 User + partner를 2회 쿼리로 조회한다.

        - SELECT user (1회)
        - SELECT partner WHERE id IN (...) (1회)
        - relationship 접근 시 추가 쿼리 0회
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        counter = QueryCounter(engine)
        try:
            counter.reset()

            stmt = select(TUser).options(selectinload(TUser.partner))
            users = list(db.scalars(stmt).all())
            query_after_list = counter.count

            partner_names = [u.partner.name for u in users if u.partner]

            total_queries = counter.count
            extra_queries = total_queries - query_after_list

            assert len(users) == 5, "사용자 5명이 조회되어야 한다"
            assert query_after_list == 2, (
                f"selectinload는 2회 쿼리로 조회해야 하는데 {query_after_list}회 실행됨"
            )
            assert extra_queries == 0, (
                f"relationship 접근 시 추가 쿼리가 0이어야 하는데 {extra_queries}회 발생함"
            )
        finally:
            counter.remove()
            db.close()

    def test_query_count_comparison(self, engine, seed_data):
        """lazy loading vs eager loading 쿼리 수를 직접 비교한다.

        N개 레코드 기준:
        - lazy (N+1):    1 + N 회
        - joinedload:    1 회 (JOIN)
        - selectinload:  2 회 (IN 서브쿼리)

        이 테스트는 세 전략의 쿼리 수 관계를 단일 어설션 블록으로 검증한다.
        """
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # --- lazy loading 쿼리 수 측정 ---
        counter_lazy = QueryCounter(engine)
        counter_lazy.reset()
        projects_lazy = list(db.scalars(select(TProject)).all())
        _ = [m.name for p in projects_lazy for m in p.models]
        lazy_count = counter_lazy.count
        counter_lazy.remove()
        db.close()

        # 세션 만료 후 재접속 (이전 identity map 캐시 제거)
        db = SessionLocal()

        # --- joinedload 쿼리 수 측정 ---
        counter_joined = QueryCounter(engine)
        counter_joined.reset()
        stmt_joined = select(TProject).options(joinedload(TProject.models))
        projects_joined = list(db.scalars(stmt_joined.distinct()).unique().all())
        _ = [m.name for p in projects_joined for m in p.models]
        joined_count = counter_joined.count
        counter_joined.remove()
        db.close()

        db = SessionLocal()

        # --- selectinload 쿼리 수 측정 ---
        counter_selectin = QueryCounter(engine)
        counter_selectin.reset()
        stmt_selectin = select(TProject).options(selectinload(TProject.models))
        projects_selectin = list(db.scalars(stmt_selectin).all())
        _ = [m.name for p in projects_selectin for m in p.models]
        selectin_count = counter_selectin.count
        counter_selectin.remove()
        db.close()

        # 쿼리 수 관계 검증
        # lazy: 1(목록) + 5(각 project.models) = 6
        # joinedload: 1 (JOIN)
        # selectinload: 2 (SELECT project + SELECT model WHERE IN)
        assert lazy_count == 6, f"lazy loading은 6회여야 하는데 {lazy_count}회임"
        assert joined_count == 1, f"joinedload는 1회여야 하는데 {joined_count}회임"
        assert selectin_count == 2, f"selectinload는 2회여야 하는데 {selectin_count}회임"

        # 핵심 관계: lazy >> selectinload > joinedload (쿼리 수 기준)
        assert lazy_count > selectin_count > joined_count, (
            f"쿼리 수 관계가 예상과 다름: lazy={lazy_count}, "
            f"selectin={selectin_count}, joined={joined_count}"
        )
