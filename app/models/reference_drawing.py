from sqlalchemy import Column, Integer, String, LargeBinary, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ReferenceDrawing(Base):
    __tablename__ = 'reference_drawing'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    elevation = Column(Float, nullable=True)
    file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')