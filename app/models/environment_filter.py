from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class EnvironmentFilter(Base):
    __tablename__ = 'environment_filter'

    part_name = Column(String, nullable=True)
    environment_id = Column(Integer, ForeignKey('model_environment.id'))

    model_environment = relationship('ModelEnvironment')