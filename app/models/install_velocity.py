from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class InstallVelocity(Base):
    __tablename__ = 'install_velocity'

    id = Column(Integer, primary_key=True, nullable=True)
    id_crane_moving_line = Column(Integer, ForeignKey('crane_moving_line.id'))
    classify = Column(Integer, nullable=True)
    begin_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    velocity = Column(Integer, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')
    crane_moving_line = relationship('CraneMovingLine')