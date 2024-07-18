from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BoomCapacity(Base):
    __tablename__ = 'boom_capacity'

    id_library = Column(Integer, ForeignKey('boom_crane_library.id_library'))
    boom_length = Column(Float, nullable=True)
    working_radius = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)

    boom_crane_library = relationship('BoomCraneLibrary')