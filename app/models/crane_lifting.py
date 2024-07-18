from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CraneLifting(Base):
    __tablename__ = 'crane_lifting'

    id = Column(Integer, primary_key=True, nullable=True)
    activation = Column(Integer, nullable=True)
    id_moving_line = Column(Integer, ForeignKey('crane_moving_line.id'))
    id_library = Column(Integer, nullable=True)
    boom_angle = Column(Float, nullable=True)
    boom_length = Column(Float, nullable=True)
    jib_length = Column(Float, nullable=True)
    working_radius = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    extra_length = Column(Float, nullable=True)
    remark = Column(String, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')
    crane_moving_line = relationship('CraneMovingLine')