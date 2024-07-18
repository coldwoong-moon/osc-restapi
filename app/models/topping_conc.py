from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ToppingConc(Base):
    __tablename__ = 'topping_conc'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    elevation = Column(Float, nullable=True)
    thick = Column(Float, nullable=True)
    pouringDate = Column(DateTime, nullable=True)
    color = Column(String, nullable=True)
    polygon_point = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, nullable=True)