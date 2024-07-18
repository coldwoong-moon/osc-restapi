from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BillOfMaterial(Base):
    __tablename__ = 'bill_of_material'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    revision = Column(Integer, nullable=True)
    create_date = Column(DateTime, nullable=True)
    regist_date = Column(DateTime, nullable=True)
    file_name = Column(String, nullable=True)
    save_file_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    number = Column(Integer, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project_model_id = Column(Integer, ForeignKey('project_model.id'))

    project = relationship('Project')
    project_model = relationship('ProjectModel')