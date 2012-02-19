import os

from scrapy.spider import BaseSpider
from scrapy.http import Request

from scraping.items import ScrapingItem

from scraping.spiders import parsers

class ParlamentoSpider(BaseSpider):
    name = 'parlamento'
    allowed_domains = (
        'www.parlamento.gub.uy',
        'www0.parlamento.gub.uy',
    )
    start_callbacks = (
        ('http://www0.parlamento.gub.uy/palacio3/p_mapaTree.asp', 'treemap'),
    )

    def __init__(self, *args, **kwargs):
        super(ParlamentoSpider, self).__init__(*args, **kwargs)
        if kwargs:
            self.start_callbacks = [(url, callback) for url, callback in kwargs.items()]

    def start_requests(self):
        for url, callback in self.start_callbacks:
            yield Request(url, getattr(parsers, callback).parse)

