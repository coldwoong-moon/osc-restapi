from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class DrawingTree(Base):
    __tablename__ = 'drawing_tree'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    drawing_div = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey('drawing_tree.id'))
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')
    drawing_tree = relationship('DrawingTree')