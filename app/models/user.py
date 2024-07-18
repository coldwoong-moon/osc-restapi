from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=True)
    email = Column(String, nullable=True)
    uuid = Column(LargeBinary, nullable=True)
    name = Column(String, nullable=True)
    password = Column(LargeBinary, nullable=True)
    partner_id = Column(Integer)
    dept = Column(String, nullable=True)
    rank = Column(String, nullable=True)
    telno = Column(String, nullable=True)
    mbtlnum = Column(String, nullable=True)
    isAccountNonExpired = Column(Integer, nullable=True)
    isAccountNonLocked = Column(Integer, nullable=True)
    isCredentialsNonExpired = Column(Integer, nullable=True)
    isEnabled = Column(Integer, nullable=True)