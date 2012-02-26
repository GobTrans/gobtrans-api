# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ValidatingItem(Item):
    """ Item subclass that calls field['validator'] when setting a field's value 
    
        
    """
    def __setitem__(self, key, value):
        if key in self.fields and 'validator' in self[key]:
            new_value = self[key]['validator'](value)
            if new_value is not None:
                value = new_value
        super(ValidatingItem, self).__setitem__(key, value)

class SubstitutesItem(ValidatingItem):
    id = Field(validator=int)
    date = Field()
    name = Field()
    chamber = Field()
    party = Field()
    substitutes = Field()
    substitutes_from = Field()
    substitutes_to = Field()
    substitutes_why = Field()


class AssistanceItem(Item):
    chamber       = Field()
    legislature   = Field()
    session       = Field()
    session_date  = Field()
    session_diary = Field()
    asistee       = Field()
    status        = Field()
    notes         = Field()

