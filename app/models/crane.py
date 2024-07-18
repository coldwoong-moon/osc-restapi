from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Crane(Base):
    __tablename__ = 'crane'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    description = Column(String, nullable=True)
    activation = Column(Integer, nullable=True)
    geometry_point = Column(String, nullable=True)
    standard_crane_id = Column(Integer, ForeignKey('standard_crane.id'))

    standard_crane = relationship('StandardCrane')