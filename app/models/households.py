from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Households(Base):
    __tablename__ = 'households'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    classify1 = Column(String, nullable=True)
    classify2 = Column(String, nullable=True)
    project_id = Column(Integer, nullable=True)