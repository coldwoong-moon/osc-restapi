from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Authority(Base):
    __tablename__ = 'authority'

    no = Column(Integer, nullable=True, primary_key=True)
    id = Column(String, nullable=True)
    authorityName = Column(String, nullable=True)