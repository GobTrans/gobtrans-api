# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class SubstitutesItem(Item):
    id = Field()
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

