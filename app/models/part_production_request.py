from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartProductionRequest(Base):
    __tablename__ = 'part_production_request'

    part_number = Column(String, primary_key=True, nullable=True)
    input_count = Column(Integer, nullable=True)
    install_prearnge_date = Column(DateTime, nullable=True)
    prdctn_posbl_date = Column(DateTime, nullable=True)
    confirm_status = Column(Integer, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')