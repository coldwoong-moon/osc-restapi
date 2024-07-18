from sqlalchemy import Column, Integer, LargeBinary, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CraneItem(Base):
    __tablename__ = 'crane_item'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    weight = Column(Float, nullable=True)
    radius = Column(Float, nullable=True)
    standard_crane_id = Column(Integer, ForeignKey('standard_crane.id'))

    standard_crane = relationship('StandardCrane')