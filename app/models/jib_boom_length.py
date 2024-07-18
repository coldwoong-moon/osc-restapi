from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class JibBoomLength(Base):
    __tablename__ = 'jib_boom_length'

    id = Column(Integer, primary_key=True, nullable=True)
    id_boom_angle = Column(Integer, ForeignKey('jib_boom_angle.id'))
    boom_length = Column(Float, nullable=True)

    jib_boom_angle = relationship('JibBoomAngle')