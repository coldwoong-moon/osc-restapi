from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ContractAmount(Base):
    __tablename__ = 'contract_amount'

    qty = Column(Float, nullable=True)
    unit_price = Column(Integer, nullable=True)
    taxitm_id = Column(Integer, primary_key=True, ForeignKey('contract_taxitm.id'))
    description = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')
    contract_taxitm = relationship('ContractTaxitm')