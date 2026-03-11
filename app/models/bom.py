from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class BillOfMaterial(Base):
    __tablename__ = "bill_of_material"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    revision = Column(Integer)
    create_date = Column(DateTime)
    regist_date = Column(DateTime)
    file_name = Column(String)
    save_file_name = Column(String)
    description = Column(Text)
    number = Column(Integer)
    project_id = Column(Integer, ForeignKey("project.id"))
    project_model_id = Column(Integer, ForeignKey("project_model.id"))

    part_quantities = relationship("PartQuantity", back_populates="bom")


class PartQuantity(Base):
    __tablename__ = "part_quantity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_model_id = Column(Integer, ForeignKey("project_model.id"))
    bom_id = Column(Integer, ForeignKey("bill_of_material.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    description = Column(Text)

    bom = relationship("BillOfMaterial", back_populates="part_quantities")


class PartMaterial(Base):
    __tablename__ = "part_material"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_number = Column(String)
    prefix = Column(String)
    qty = Column(Integer)
    hold_qty = Column(Integer)
    available_qty = Column(Integer)
    volume = Column(Float)
    sum_volume = Column(Float)
    strength = Column(String)
    width = Column(Float)
    height = Column(Float)
    length = Column(Float)
    project_model_id = Column(Integer, ForeignKey("project_model.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    renewal_time = Column(DateTime)
