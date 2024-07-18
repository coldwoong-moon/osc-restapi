from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartInfo(Base):
    __tablename__ = 'part_info'

    guid = Column(String, primary_key=True, nullable=True)
    aptcmpl_id = Column(Integer, ForeignKey('apartment_complex.id'))
    floor_id = Column(Integer, ForeignKey('floor.id'))
    zone_id = Column(Integer, ForeignKey('zone.id'))
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))
    renewal_time = Column(DateTime, nullable=True)

    apartment_complex = relationship('ApartmentComplex')
    zone = relationship('Zone')
    floor = relationship('Floor')
    project_model = relationship('ProjectModel')
    project = relationship('Project')