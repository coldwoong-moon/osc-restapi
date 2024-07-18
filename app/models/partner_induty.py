from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PartnerInduty(Base):
    __tablename__ = 'partner_induty'

    partner_id = Column(Integer, primary_key=True, ForeignKey('partner.id'))
    induty_id = Column(Integer, primary_key=True, ForeignKey('induty.id'))

    induty = relationship('Induty')
    partner = relationship('Partner')