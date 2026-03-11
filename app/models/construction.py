from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConstructionPlan(Base):
    __tablename__ = "construction_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(String)
    name = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))


class ConstructionDueDate(Base):
    __tablename__ = "construction_due_date"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    begin_date = Column(DateTime)
    end_date = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))
