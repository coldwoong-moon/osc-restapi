from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CalendarSetting(Base):
    __tablename__ = 'calendar_setting'

    id = Column(Integer, primary_key=True, nullable=True)
    name = Column(String, nullable=True)
    holyday_date = Column(DateTime, nullable=True)
    id_project = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project')