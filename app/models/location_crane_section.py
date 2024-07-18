from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class LocationCraneSection(Base):
    __tablename__ = 'location_crane_section'

    id = Column(Integer, primary_key=True, nullable=True)
    id_crane_section = Column(Integer, ForeignKey('crane_section.id'))
    location = Column(String, nullable=True)
    activation = Column(Integer, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')
    crane_section = relationship('CraneSection')