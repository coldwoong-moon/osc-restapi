from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    cnstrct_begin_date = Column(DateTime)
    cnstrct_end_date = Column(DateTime)
    first_cnstrct_date = Column(DateTime)
    manager_id = Column(Integer)
    delete_status = Column(Boolean, default=False)
    renewal_time = Column(DateTime)

    models = relationship("ProjectModel", back_populates="project")


class ProjectModel(Base):
    __tablename__ = "project_model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    name = Column(String)
    description = Column(String)
    project_id = Column(Integer, ForeignKey("project.id"))
    renewal_time = Column(DateTime)

    project = relationship("Project", back_populates="models")


class ProjectUser(Base):
    __tablename__ = "project_user"

    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"))
