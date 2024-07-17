from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR, Column

Base = declarative_base()


class Authority(Base):
    __tablename__ = "authority"

    id = Column(VARCHAR(50), nullable=True, primary_key=True)
    authorityName: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
