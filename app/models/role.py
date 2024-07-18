from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)