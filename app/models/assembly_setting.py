from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class AssemblySetting(Base):
    __tablename__ = 'assembly_setting'

    id = Column(Integer, primary_key=True, nullable=True)
    install_order = Column(Integer, nullable=True)
    assembly_classify = Column(Integer, nullable=True)
    install_velocity = Column(Integer, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')