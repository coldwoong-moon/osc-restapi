from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CraneLibrary(Base):
    __tablename__ = 'crane_library'

    id = Column(Integer, nullable=True)
    crane_weight = Column(String, nullable=True)
    name = Column(String, nullable=True)
    crane_type = Column(String, nullable=True)
    crane_category = Column(Integer, nullable=True)
    attachment_type = Column(Integer, nullable=True)
    rotate_x = Column(Float, nullable=True)
    rotate_y = Column(Float, nullable=True)
    boom_angle_min = Column(Float, nullable=True)
    boom_angle_max = Column(Float, nullable=True)
    counterweight = Column(Float, nullable=True)
    carbody = Column(Float, nullable=True)
    order_idx = Column(Integer, nullable=True)
    remark = Column(String, nullable=True)