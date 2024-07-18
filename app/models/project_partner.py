from sqlalchemy import Column, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ProjectPartner(Base):
    __tablename__ = 'project_partner'

    id = Column(Integer, primary_key=True, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    partner_id = Column(Integer, ForeignKey('partner.id'))

    project = relationship('Project')
    partner = relationship('Partner')