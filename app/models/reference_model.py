from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ReferenceModel(Base):
    __tablename__ = 'reference_model'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)
    regist_date = Column(DateTime, nullable=True)
    user_name = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')