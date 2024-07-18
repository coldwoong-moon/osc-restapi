from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class EnvironmentPrefix(Base):
    __tablename__ = 'environment_prefix'

    prefix = Column(String, nullable=True)
    part_div = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
    environment_id = Column(Integer, ForeignKey('model_environment.id'))

    model_environment = relationship('ModelEnvironment')