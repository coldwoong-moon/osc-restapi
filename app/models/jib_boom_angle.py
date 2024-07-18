from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class JibBoomAngle(Base):
    __tablename__ = 'jib_boom_angle'

    id = Column(Integer, primary_key=True, nullable=True)
    id_library = Column(Integer, ForeignKey('crane_library.id'))
    boom_angle = Column(Float, nullable=True)
    jib_angle_min = Column(Float, nullable=True)
    jib_angle_max = Column(Float, nullable=True)
    drawing_file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)

    crane_library = relationship('CraneLibrary')