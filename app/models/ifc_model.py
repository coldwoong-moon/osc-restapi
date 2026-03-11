from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class IFCModel(Base):
    __tablename__ = "ifc_model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    project_model_id = Column(Integer, ForeignKey("project_model.id"), nullable=False)
    revision = Column(Integer, nullable=False, default=0)
    number = Column(Integer, nullable=False, default=0)
    file_name = Column(String(500), nullable=False)
    saved_file_name = Column(String(500), nullable=False)
    description = Column(String(2000))
    model_type = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    create_date = Column(DateTime)
    regist_date = Column(DateTime, server_default=func.now())
