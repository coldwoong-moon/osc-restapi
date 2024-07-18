from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ModelEnvironment(Base):
    __tablename__ = 'model_environment'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    prefix_separator = Column(String, nullable=True)
    guid = Column(String, nullable=True)
    prefix_id = Column(String, nullable=True)
    material = Column(String, nullable=True)
    material_type = Column(String, nullable=True)
    prefix = Column(String, nullable=True)
    project_model_id = Column(Integer, ForeignKey('project_model.id'))

    project_model = relationship('ProjectModel')