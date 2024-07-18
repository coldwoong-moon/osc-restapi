from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class EnvironmentMaterial(Base):
    __tablename__ = 'environment_material'

    material_type = Column(String, primary_key=True, nullable=True)
    name = Column(String, nullable=True)
    environment_id = Column(Integer, primary_key=True, ForeignKey('model_environment.id'))

    model_environment = relationship('ModelEnvironment')