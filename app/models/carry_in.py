from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class CarryInRequest(Base):
    __tablename__ = "carry_in_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(LargeBinary)
    guid = Column(String)
    title = Column(String)
    status = Column(Integer)
    request_date = Column(DateTime)
    project_id = Column(Integer, ForeignKey("project.id"))

    items = relationship("CarryInRequestItem", back_populates="carry_in_request")


class CarryInRequestItem(Base):
    __tablename__ = "carry_in_request_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carry_in_request_id = Column(Integer, ForeignKey("carry_in_request.id"))
    part_number = Column(String)
    quantity = Column(Integer)

    carry_in_request = relationship("CarryInRequest", back_populates="items")
