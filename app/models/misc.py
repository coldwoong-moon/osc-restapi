from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class Households(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    aptcmpl_id = Column(Integer, ForeignKey("apartment_complex.id"))
    project_id = Column(Integer, ForeignKey("project.id"))

    apartment_complex = relationship("ApartmentComplex", foreign_keys=[aptcmpl_id])


class Partner(Base):
    __tablename__ = "partner"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    business_number = Column(String)


class Marker(Base):
    __tablename__ = "marker"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("project.id"))


class ModelEnvironment(Base):
    __tablename__ = "model_environment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))


class ModelScene(Base):
    __tablename__ = "model_scene"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    data = Column(Text)
    project_id = Column(Integer, ForeignKey("project.id"))
