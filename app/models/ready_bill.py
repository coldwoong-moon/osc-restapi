from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ReadyBill(Base):
    __tablename__ = 'ready_bill'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    bill_start_date = Column(DateTime, nullable=True)
    bill_end_date = Column(DateTime, nullable=True)
    monthly_start_date = Column(DateTime, nullable=True)
    monthly_end_date = Column(DateTime, nullable=True)
    bill_description = Column(String, nullable=True)
    monthly_description = Column(String, nullable=True)
    direct_rate = Column(Float, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')