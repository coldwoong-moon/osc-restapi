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
            _ = p.children
        assert self.query_count > 1

    def test_joinedload_reduces_queries(self):
        self.query_count = 0
        parents = self.db.query(Parent).options(joinedload(Parent.children)).all()
        for p in parents:
            _ = p.children
        assert self.query_count == 1

    def test_selectinload_reduces_queries(self):
        self.query_count = 0
        parents = self.db.query(Parent).options(selectinload(Parent.children)).all()
        for p in parents:
            _ = p.children
        assert self.query_count <= 2
