from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ProjectUser(Base):
    __tablename__ = 'project_user'

    project_id = Column(Integer, primary_key=True, ForeignKey('project.id'))
    user_id = Column(Integer, primary_key=True, ForeignKey('user.id'))
    role_id = Column(Integer, primary_key=True, ForeignKey('role.id'))

    project = relationship('Project')
    user = relationship('User')
    role = relationship('Role')