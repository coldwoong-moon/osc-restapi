from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductionCompleted(Base):
    __tablename__ = 'production_completed'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    part_number = Column(String, nullable=True)
    completed_qty = Column(Integer, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    rfid_id = Column(String, nullable=True)
    project_id = Column(Integer, nullable=True)