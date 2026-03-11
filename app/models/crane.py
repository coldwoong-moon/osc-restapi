from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class StandardCrane(Base):
    __tablename__ = "standard_crane"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    color = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))

    crane_items = relationship("CraneItem", back_populates="standard_crane")
    cranes = relationship("Crane", back_populates="standard_crane")


class CraneItem(Base):
    __tablename__ = "crane_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    weight = Column(Float)
    radius = Column(Float)
    standard_crane_id = Column(Integer, ForeignKey("standard_crane.id"))

    standard_crane = relationship("StandardCrane", back_populates="crane_items")


class Crane(Base):
    __tablename__ = "crane"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    description = Column(String)
    activation = Column(Boolean)
    geometry_point = Column(Text)
    standard_crane_id = Column(Integer, ForeignKey("standard_crane.id"))

    standard_crane = relationship("StandardCrane", back_populates="cranes")
