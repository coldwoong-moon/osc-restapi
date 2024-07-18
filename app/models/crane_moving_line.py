from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CraneMovingLine(Base):
    __tablename__ = 'crane_moving_line'

    id = Column(Integer, primary_key=True, nullable=True)
    name = Column(String, nullable=True)
    activation = Column(Integer, nullable=True)
    color = Column(String, nullable=True)
    points = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    qty_span = Column(Integer, nullable=True)
    running_method = Column(Integer, nullable=True)
    remark = Column(String, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')