# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
from datetime import datetime

from scrapy.item import Item, Field

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

class SubstitutesItem(ValidatingItem):
    id = Field(validator=int, required=True)
    date = Field()
    name = Field()
    chamber = Field()
    party = Field()
    substitutes = Field()
    substitutes_from = Field()
    substitutes_to = Field()
    substitutes_why = Field()


def chamber_validator(chamber):
    if chamber not in ('S', 'D'):
        raise ValueError('chamber=%s' % chamber)

def session_date_validator(session_date):
    return datetime.strptime(session_date, '%d/%m/%Y').date().isoformat()

def url_validator(session_diary):
    if session_diary is not None and not session_diary.startswith('http'):
        raise ValueError('session_diary=%s' % session_diary)

def status_validator(status):
    if status not in ('present', 'warned', 'unwarned', 'license'):
        raise ValueError('status=%s' % status)

class AssistanceItem(ValidatingItem):
    chamber       = Field(validator=chamber_validator, required=True)
    legislature   = Field(validator=int, required=True)
    session       = Field(validator=int, required=True)
    session_date  = Field(validator=session_date_validator, required=True)
    session_diary = Field(validator=url_validator)
    asistee       = Field(required=True)
    status        = Field(validator=status_validator, required=True)
    notes         = Field()

