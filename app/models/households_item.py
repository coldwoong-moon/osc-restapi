from sqlalchemy import Column, Integer, String, LargeBinary, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class HouseholdsItem(Base):
    __tablename__ = 'households_item'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    elevation = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    polygon_point = Column(String, nullable=True)
    households_id = Column(Integer, ForeignKey('households.id'))
    project_id = Column(Integer, nullable=True)

    households = relationship('Households')