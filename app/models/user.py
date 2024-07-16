from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import BINARY, BLOB, INTEGER, VARCHAR, Column, LargeBinary

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(INTEGER, primary_key=True, index=True)
    email = Column(VARCHAR(50), unique=True)
    uuid = Column(LargeBinary)
    name = Column(VARCHAR(50))
    password = Column(BLOB)
    partner_id = Column(INTEGER)
    dept = Column(VARCHAR(50))
    rank = Column(VARCHAR(20))
    telno = Column(VARCHAR(20))
    mbtlnum = Column(VARCHAR(20))
    isAccountNonExpired = Column(INTEGER)
    isAccountNonLocked = Column(INTEGER)
    isCredentialsNonExpired = Column(INTEGER)
    isEnabled = Column(INTEGER)
