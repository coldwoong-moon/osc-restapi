from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BoomCraneLibrary(Base):
    __tablename__ = 'boom_crane_library'

    id_library = Column(Integer, primary_key=True, ForeignKey('crane_library.id'))
    fixed_jib_min_angle = Column(Float, nullable=True)
    fixed_jib_max_angle = Column(Float, nullable=True)
    fixed_jib_length = Column(Float, nullable=True)
    drawing_file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)

    crane_library = relationship('CraneLibrary')