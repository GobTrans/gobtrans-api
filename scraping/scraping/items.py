# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class SubstitutesItem(Item):
    name = Field()
    chamber = Field()
    party = Field()
    substitutes = Field()
    substitutes_from = Field()
    substitutes_to = Field()
    substitutes_why = Field()
    
