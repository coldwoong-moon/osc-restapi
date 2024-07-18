from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartMaterial(Base):
    __tablename__ = 'part_material'

    part_number = Column(String, primary_key=True, nullable=True)
    prefix = Column(String, nullable=True)
    qty = Column(Float, nullable=True)
    hold_qty = Column(Integer, nullable=True)
    available_qty = Column(Integer, nullable=True)
    volume = Column(Float, nullable=True)
    sum_volume = Column(Float, nullable=True)
    strength = Column(String, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    length = Column(Float, nullable=True)
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')
    project_model = relationship('ProjectModel')