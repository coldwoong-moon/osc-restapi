from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Grid(Base):
    __tablename__ = 'grid'

    label = Column(String, nullable=True)
    plane_name = Column(String, nullable=True)
    start_point = Column(String, nullable=True)
    end_point = Column(String, nullable=True)
    visible = Column(Integer, nullable=True)
    revision = Column(Integer, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project_model_id = Column(Integer, ForeignKey('project_model.id'))

    project = relationship('Project')
    project_model = relationship('ProjectModel')