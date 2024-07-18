from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Partner(Base):
    __tablename__ = 'partner'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    renewal_time = Column(DateTime, nullable=True)