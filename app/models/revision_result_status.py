from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class RevisionResultStatus(Base):
    __tablename__ = 'revision_result_status'

    compare_status = Column(Integer, nullable=True)
    compare_result_id = Column(Integer, ForeignKey('revision_compare_result.id'))

    revision_compare_result = relationship('RevisionCompareResult')