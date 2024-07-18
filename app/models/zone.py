from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Zone(Base):
    __tablename__ = 'zone'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    end_date = Column(DateTime, nullable=True)
    color = Column(String, nullable=True)
    polygon_point = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')