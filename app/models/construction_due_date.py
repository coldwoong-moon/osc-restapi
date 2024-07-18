from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ConstructionDueDate(Base):
    __tablename__ = 'construction_due_date'

    guid = Column(String, primary_key=True, nullable=True)
    due_date = Column(DateTime, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')
    project_model = relationship('ProjectModel')