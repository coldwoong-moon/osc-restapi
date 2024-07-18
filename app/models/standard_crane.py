from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class StandardCrane(Base):
    __tablename__ = 'standard_crane'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    color = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')