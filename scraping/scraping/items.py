# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
from datetime import datetime, date

from scrapy.item import BaseItem
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates, relationship

AlchemyBase = declarative_base()

class PrintableItem(BaseItem):
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        colnames = (col.name for col in self.__table__.columns)
        res = []
        for item in ((col, getattr(self, col)) for col in colnames):
            res.append("%s=%s" % item)
        return "<%s %s>" % (self.__class__.__name__, ", ".join(res))



class SubstitutesItem(PrintableItem, AlchemyBase):
    __tablename__ = 'substitutes'

    id = Column(Integer, primary_key=True)
    legislature_id = Column(Integer)
    original_id = Column(Integer)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    chamber = Column(Enum('S', 'D'))
    party = Column(String)
    substitutes_line = Column(String)

    @validates('date')
    def validate_date(self, key, value):
        assert isinstance(value, date)
        return value


class AssistanceNote(AlchemyBase):
    __tablename__ = 'assistance_notes'

    id            = Column(Integer, primary_key=True)
    note          = Column(String, nullable=False)
    assistance_id = Column(Integer, ForeignKey('assistances.id'), nullable=False)

class AssistanceItem(PrintableItem, AlchemyBase):
    __tablename__ = 'assistances'

    id            = Column(Integer, primary_key=True)
    chamber       = Column(Enum('S', 'D'), nullable=False)
    legislature   = Column(Integer, nullable=False)
    session       = Column(Integer, nullable=False)
    session_date  = Column(Date, nullable=False)
    session_diary = Column(String)
    asistee       = Column(String, nullable=False)
    status        = Column(Enum('present', 'absent_w_warn', 'absent_wo_warn', 'on_vacation'), nullable=False)
    notes         = relationship('AssistanceNote', backref='assistance')

    @validates('session_date')
    def session_date_validator(self, key, value):
        return datetime.strptime(value, '%d/%m/%Y').date()

    @validates('session_diary')
    def url_validator(self, key, value):
        if value is not None and not value.startswith('http'):
            raise ValueError('session_diary=%s' % value)

