from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    partner_id = Column(Integer, ForeignKey("partner.id"), nullable=True)
    dept = Column(String)
    rank = Column(String)
    telno = Column(String)
    mbtlnum = Column(String)
    isAccountNonExpired = Column(Boolean)
    isAccountNonLocked = Column(Boolean)
    isCredentialsNonExpired = Column(Boolean)
    isEnabled = Column(Boolean)

    partner = relationship("Partner", foreign_keys=[partner_id])


class Authority(Base):
    __tablename__ = "authority"

    no = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    authorityName = Column(String)


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
