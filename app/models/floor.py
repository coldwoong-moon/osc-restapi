from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Floor(Base):
    __tablename__ = 'floor'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    aptcmpl_id = Column(Integer, ForeignKey('apartment_complex.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    renewal_time = Column(DateTime, nullable=True)

    apartment_complex = relationship('ApartmentComplex')
    project = relationship('Project')