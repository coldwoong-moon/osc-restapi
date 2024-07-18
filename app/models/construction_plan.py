from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ConstructionPlan(Base):
    __tablename__ = 'construction_plan'

    guid = Column(String, primary_key=True, nullable=True)
    plan_date = Column(DateTime, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')