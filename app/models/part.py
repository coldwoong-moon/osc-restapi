from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PartInfo(Base):
    __tablename__ = "part_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(String, unique=True)
    aptcmpl_id = Column(Integer, ForeignKey("apartment_complex.id"), nullable=True)
    floor_id = Column(Integer, ForeignKey("floor.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zone.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"))
    renewal_time = Column(DateTime)

    apartment_complex = relationship("ApartmentComplex", foreign_keys=[aptcmpl_id])
    floor = relationship("Floor", foreign_keys=[floor_id])
    zone = relationship("Zone", foreign_keys=[zone_id])


class PartAttribute(Base):
    __tablename__ = "part_attribute"

    part_number = Column(String, primary_key=True)
    volume = Column(Float)
    ton = Column(Float)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)


class PartProductionRequest(Base):
    __tablename__ = "part_production_request"

    part_number = Column(String, primary_key=True)
    input_count = Column(Integer)
    install_prearnge_date = Column(String)
    prdctn_posbl_date = Column(String)
    confirm_status = Column(Integer)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
