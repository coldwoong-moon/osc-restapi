from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class AssemblyInfo(Base):
    __tablename__ = "assembly_info"

    guid = Column(String, primary_key=True)
    assembly_number = Column(String)
    classify = Column(Integer)
    classify_name = Column(String)
    width = Column(Float)
    height = Column(Float)
    length = Column(Float)
    volume = Column(Float)
    weight = Column(Float)
    project_id = Column(Integer, ForeignKey("project.id"))
    revision = Column(Integer)
    number = Column(Integer)
    project_model_id = Column(Integer, ForeignKey("project_model.id"))
    structure_id = Column(Integer, nullable=True)
    floor_id = Column(Integer, ForeignKey("floor.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zone.id"), nullable=True)
    updated_at = Column(DateTime)

    floor = relationship("Floor", foreign_keys=[floor_id])
    zone = relationship("Zone", foreign_keys=[zone_id])
