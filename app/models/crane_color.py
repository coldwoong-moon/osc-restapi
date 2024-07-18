from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CraneColor(Base):
    __tablename__ = 'crane_color'

    crane_status = Column(Integer, primary_key=True, nullable=True)
    color = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')