from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BillAmount(Base):
    __tablename__ = 'bill_amount'

    qty = Column(Float, nullable=True)
    unit_price = Column(Integer, nullable=True)
    taxitm_id = Column(Integer, primary_key=True, ForeignKey('contract_taxitm.id'))
    description = Column(String, nullable=True)
    bill_id = Column(Integer, primary_key=True, ForeignKey('ready_bill.id'))

    contract_taxitm = relationship('ContractTaxitm')
    ready_bill = relationship('ReadyBill')