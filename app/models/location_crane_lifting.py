from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class LocationCraneLifting(Base):
    __tablename__ = 'location_crane_lifting'

    id = Column(Integer, primary_key=True, nullable=True)
    id_crane_lifting = Column(Integer, ForeignKey('crane_lifting.id'))
    location = Column(String, nullable=True)
    activation = Column(Integer, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    crane_lifting = relationship('CraneLifting')
    project = relationship('Project')