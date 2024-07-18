from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class InstallCompleted(Base):
    __tablename__ = 'install_completed'

    guid = Column(String, primary_key=True, nullable=True)
    install_date = Column(DateTime, nullable=True)
    rfid_id = Column(String, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))

    project = relationship('Project')
    project_model = relationship('ProjectModel')