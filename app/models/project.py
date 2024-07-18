from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    cnstrct_begin_date = Column(DateTime, nullable=True)
    cnstrct_end_date = Column(DateTime, nullable=True)
    first_cnstrct_date = Column(DateTime, nullable=True)
    manager_id = Column(Integer, nullable=True)
    delete_status = Column(Integer, nullable=True)
    renewal_time = Column(DateTime, nullable=True)