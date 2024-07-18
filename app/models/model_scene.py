from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ModelScene(Base):
    __tablename__ = 'model_scene'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    scene_data = Column(String, nullable=True)
    project_id = Column(Integer, nullable=True)