from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class DrawingTree(Base):
    __tablename__ = "drawing_tree"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    drawing_div = Column(Integer)
    depth = Column(Integer)
    parent_id = Column(Integer, ForeignKey("drawing_tree.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"))

    children = relationship("DrawingTree", foreign_keys=[parent_id])
    drawings = relationship("Drawing", back_populates="drawing_tree")


class Drawing(Base):
    __tablename__ = "drawing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    revision = Column(Integer)
    create_date = Column(DateTime)
    regist_date = Column(DateTime)
    file_name = Column(String)
    save_file_name = Column(String)
    description = Column(Text)
    number = Column(Integer)
    drawing_tree_id = Column(Integer, ForeignKey("drawing_tree.id"))
    project_id = Column(Integer, ForeignKey("project.id"))

    drawing_tree = relationship("DrawingTree", back_populates="drawings")


class ReferenceDrawing(Base):
    __tablename__ = "reference_drawing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    elevation = Column(Float)
    file_name = Column(String)
    save_file_name = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))
