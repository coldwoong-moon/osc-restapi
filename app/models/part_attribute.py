from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartAttribute(Base):
    __tablename__ = 'part_attribute'

    part_number = Column(String, primary_key=True, nullable=True)
    volume = Column(Float, nullable=True)
    ton = Column(Float, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')