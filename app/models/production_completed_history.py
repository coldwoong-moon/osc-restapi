from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ProductionCompletedHistory(Base):
    __tablename__ = 'production_completed_history'

    id = Column(Integer, primary_key=True, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    part_number = Column(String, nullable=True)
    qty = Column(Integer, nullable=True)
    renewal_type = Column(Integer, nullable=True)
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')