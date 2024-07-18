from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Induty(Base):
    __tablename__ = 'induty'

    id = Column(Integer, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)