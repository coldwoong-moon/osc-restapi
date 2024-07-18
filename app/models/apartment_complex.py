from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ApartmentComplex(Base):
    __tablename__ = 'apartment_complex'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')