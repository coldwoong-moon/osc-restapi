from sqlalchemy import Column, Integer, String, LargeBinary, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Dimension(Base):
    __tablename__ = 'dimension'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    axis_x_point = Column(String, nullable=True)
    axis_y_point = Column(String, nullable=True)
    extension_line_point1 = Column(String, nullable=True)
    extension_line_point2 = Column(String, nullable=True)
    line_point = Column(String, nullable=True)
    text_height = Column(Float, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')