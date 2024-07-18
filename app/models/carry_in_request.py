from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CarryInRequest(Base):
    __tablename__ = 'carry_in_request'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    registDate = Column(DateTime, nullable=True)
    carryinDate = Column(DateTime, nullable=True)
    code = Column(String, nullable=True)
    order_id = Column(Integer, nullable=True)
    remark = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, nullable=True)