from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AssemblyInfo(Base):
    __tablename__ = 'assembly_info'

    guid = Column(String, primary_key=True, nullable=True)
    assembly_number = Column(String, nullable=True)
    classify = Column(Integer, nullable=True)
    classify_name = Column(String, nullable=True)
    strength = Column(String, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    length = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    project_id = Column(Integer, primary_key=True, nullable=True)
    revision = Column(Integer, nullable=True)
    number = Column(Integer, nullable=True)
    project_modeL_id = Column(Integer, nullable=True)
    renewal_time = Column(DateTime, nullable=True)