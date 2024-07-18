from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CarryInRequestItem(Base):
    __tablename__ = 'carry_in_request_item'

    guid = Column(String, primary_key=True, nullable=True)
    part_number = Column(String, nullable=True)
    carry_in_time = Column(String, nullable=True)
    request_id = Column(Integer, ForeignKey('carry_in_request.id'))
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    project_model_id = Column(Integer, primary_key=True, ForeignKey('project_model.id'))

    project = relationship('Project')
    carry_in_request = relationship('CarryInRequest')
    project_model = relationship('ProjectModel')