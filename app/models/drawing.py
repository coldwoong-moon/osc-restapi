from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Drawing(Base):
    __tablename__ = 'drawing'

    name = Column(String, primary_key=True, nullable=True)
    revision = Column(Integer, primary_key=True, nullable=True)
    create_date = Column(DateTime, nullable=True)
    regist_date = Column(DateTime, nullable=True)
    file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    number = Column(Integer, primary_key=True, nullable=True)
    drawing_tree_id = Column(Integer, ForeignKey('drawing_tree.id'))
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')
    drawing_tree = relationship('DrawingTree')