from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class RevisionCompareResult(Base):
    __tablename__ = 'revision_compare_result'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    part_number = Column(String, nullable=True)
    guid = Column(String, nullable=True)
    part_div = Column(Integer, nullable=True)
    source_revision = Column(Integer, nullable=True)
    target_revision = Column(Integer, nullable=True)
    project_model_id = Column(Integer, ForeignKey('project_model.id'))
    revision_id = Column(Integer, ForeignKey('revision.id'))

    revision = relationship('Revision')
    project_model = relationship('ProjectModel')