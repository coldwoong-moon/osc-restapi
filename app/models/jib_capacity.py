from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class JibCapacity(Base):
    __tablename__ = 'jib_capacity'

    id_boom_length = Column(Integer, ForeignKey('jib_boom_length.id'))
    jib_length = Column(Float, nullable=True)
    working_radius = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)

    jib_boom_length = relationship('JibBoomLength')