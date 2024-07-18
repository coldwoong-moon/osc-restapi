from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ContractTaxitm(Base):
    __tablename__ = 'contract_taxitm'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    cntrct_taxitm_type_id = Column(Integer, nullable=True)
    view_type = Column(Integer, nullable=True)
    input_type = Column(Integer, nullable=True)
    view_order = Column(Integer, nullable=True)
    custom_status = Column(Integer, nullable=True)
    unit = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey('contract_taxitm.id'))
    expitm_id = Column(Integer, ForeignKey('contract_expitm.id'))
    project_id = Column(Integer, ForeignKey('project.id'))

    contract_taxitm = relationship('ContractTaxitm')
    contract_expitm = relationship('ContractExpitm')
    project = relationship('Project')