from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartQuantity(Base):
    __tablename__ = 'part_quantity'

    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))
    bom_id = Column(Integer, ForeignKey('bill_of_material.id'))
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    description = Column(String, nullable=True)

    project = relationship('Project')
    bill_of_material = relationship('BillOfMaterial')
    project_model = relationship('ProjectModel')