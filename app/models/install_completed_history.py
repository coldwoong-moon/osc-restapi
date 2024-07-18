from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class InstallCompletedHistory(Base):
    __tablename__ = 'install_completed_history'

    guid = Column(String, primary_key=True, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))
    renewal_type = Column(Integer, nullable=True)
    renewal_time = Column(DateTime, nullable=True)

    project = relationship('Project')
    project_model = relationship('ProjectModel')