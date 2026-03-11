from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class ApartmentComplex(Base):
    __tablename__ = "apartment_complex"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))

    floors = relationship("Floor", back_populates="apartment_complex")


class Floor(Base):
    __tablename__ = "floor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(String)
    name = Column(String)
    aptcmpl_id = Column(Integer, ForeignKey("apartment_complex.id"))
    project_id = Column(Integer, ForeignKey("project.id"))

    apartment_complex = relationship("ApartmentComplex", back_populates="floors")


class Zone(Base):
    __tablename__ = "zone"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    end_date = Column(DateTime)
    color = Column(String)
    polygon_point = Column(Text)
    project_id = Column(Integer, ForeignKey("project.id"))
    renewal_time = Column(DateTime)
