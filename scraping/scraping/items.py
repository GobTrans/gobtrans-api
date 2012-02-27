# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
from datetime import datetime, date

from scrapy.item import BaseItem, Item, Field
from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

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
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    chamber = Column(Enum('S', 'D'))
    party = Column(String)
    substitutes_line = Column(String)

    @validates('date')
    def validate_date(self, key, value):
        assert isinstance(value, date)
        return value

class ValidatingItem(Item):
    def __init__(self, *args, **kwargs):
        super(ValidatingItem, self).__init__(*args, **kwargs)
        for name, field in self.fields.iteritems():
            if 'required' in field and field['required'] and name not in self._values:
                raise ValueError("Field %s is required" % name)

    def __setitem__(self, key, value):
        if key in self.fields and 'validator' in self.fields[key]:
            new_value = self.fields[key]['validator'](value)
            if new_value is not None:
                value = new_value
        super(ValidatingItem, self).__setitem__(key, value)


class AssistanceItem(PrintableItem, AlchemyBase):
    __tablename__ = 'assistance'

    id            = Column(Integer, primary_key=True)
    chamber       = Column(Enum('S', 'D'), nullable=False)
    legislature   = Column(Integer, nullable=False)
    session       = Column(Integer, nullable=False)
    session_date  = Column(Date, nullable=False)
    session_diary = Column(String)
    asistee       = Column(String, nullable=False)
    status        = Column(Enum('present', 'warned', 'unwarned', 'license'), nullable=False)
    notes         = Column(String)

    @validates('session_date')
    def session_date_validator(self, key, value):
        return datetime.strptime(value, '%d/%m/%Y').date()

    @validates('session_diary')
    def url_validator(self, key, value):
        if value is not None and not value.startswith('http'):
            raise ValueError('session_diary=%s' % value)

