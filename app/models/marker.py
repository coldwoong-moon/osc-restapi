from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Marker(Base):
    __tablename__ = 'marker'

    name = Column(String, primary_key=True, nullable=True)
    description = Column(String, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    radius = Column(Float, nullable=True)
    text_height = Column(Float, nullable=True)
    geometry_point = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')