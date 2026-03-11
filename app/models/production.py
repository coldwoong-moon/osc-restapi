from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, LargeBinary

from app.db.base import Base


class ProductionCompleted(Base):
    __tablename__ = "production_completed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    part_number = Column(String)
    completed_date = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))


class InstallCompleted(Base):
    __tablename__ = "install_completed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    part_number = Column(String)
    completed_date = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))
