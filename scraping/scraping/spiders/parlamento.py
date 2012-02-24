# -*- coding: utf-8 -*-
import os
from functools import partial
from scrapy.spider import BaseSpider
from scrapy.http import Request

from scraping.spiders import parsers

class ParlamentoSpider(BaseSpider):
    name = 'parlamento'
    allowed_domains = (
        'www.parlamento.gub.uy',
        'www0.parlamento.gub.uy',
    )
    start_callbacks = (
        #('http://www0.parlamento.gub.uy/palacio3/p_mapaTree.asp', 'assistance'),
        ('http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=S', 'substitutes'),
        #('http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=D', 'substitutes'),
        #('http://www0.parlamento.gub.uy/palacio3/legisladores_der.asp', 'parliamentaries'),
    )

    def __init__(self, *args, **kwargs):
        super(ParlamentoSpider, self).__init__(*args, **kwargs)
        if kwargs:
            self.start_callbacks = [(url, callback) for url, callback in kwargs.items()]

    def start_requests(self):
        for url, parser in self.start_callbacks:
            yield Request(url, partial(getattr(parsers, parser).parse, self))
