from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartStatus(Base):
    __tablename__ = 'part_status'

    guid = Column(String, primary_key=True, nullable=True)
    prdctn_request_date = Column(DateTime, nullable=True)
    prdctn_compt_date = Column(DateTime, nullable=True)
    shipment_date = Column(DateTime, nullable=True)
    takein_compt_date = Column(DateTime, nullable=True)
    install_compt_date = Column(DateTime, nullable=True)
    current_status = Column(Integer, nullable=True)
    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))

    project = relationship('Project')