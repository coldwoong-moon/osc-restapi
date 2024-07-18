from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ContractExpitm(Base):
    __tablename__ = 'contract_expitm'

    id = Column(Integer, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    view_order = Column(Integer, nullable=True)