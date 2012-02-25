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
    start_callbacks = {
        'assistance': (
            'http://www0.parlamento.gub.uy/palacio3/p_mapaTree.asp',
        ),
        'substitutes': (
            'http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=S',
            'http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=D',
        ),
        'parliamentaries': (
            'http://www0.parlamento.gub.uy/palacio3/legisladores_der.asp',
        ),
    }

    def __init__(self, *args, **kwargs):
        super(ParlamentoSpider, self).__init__(*args, **kwargs)
        if 'enable' in kwargs:
            enabled = kwargs['enable'].split(',')
            self.start_callbacks = dict(
                (parser, urls) for parser, urls in self.start_callbacks.items() if parser in enabled
            )
        elif 'disable' in kwargs:
            disabled = kwargs['disable'].split(',')
            self.start_callbacks = dict(
                (parser, urls) for parser, urls in self.start_callbacks.items() if parser not in disabled
            )

    def start_requests(self):
        for parser, urls in self.start_callbacks.items():
            callback = partial(getattr(parsers, parser).parse, self)
            for url in urls:
                yield Request(url, callback)

