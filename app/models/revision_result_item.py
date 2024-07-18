from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class RevisionResultItem(Base):
    __tablename__ = 'revision_result_item'

    guid = Column(String, nullable=True)
    name = Column(String, nullable=True)
    source = Column(String, nullable=True)
    target = Column(String, nullable=True)
    compare_item = Column(Integer, nullable=True)
    item_type = Column(Integer, nullable=True)
    compare_result_id = Column(Integer, ForeignKey('revision_compare_result.id'))

    revision_compare_result = relationship('RevisionCompareResult')