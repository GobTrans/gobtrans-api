# -*- coding: utf-8 -*-
import os
import datetime
import types
from functools import partial
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.conf import settings

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

        date_start = settings['SCRAPER_DATE_START']
        date_end = settings['SCRAPER_DATE_END']
        if 'start' in kwargs:
            date_start = kwargs['start']
        if 'end' in kwargs:
            date_end = kwargs['end']
        self.date_start = self._get_date(date_start)
        self.date_end = self._get_date(date_end)

    def _get_date(self, value):
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        if type(value) in types.StringTypes:
            return datetime.datetime.strptime(value, settings['DATE_FMT']).date()
        raise ValueError("Invalid date value: %s. Must be one of datetime.date, datetime.datetime or '%s' string." % \
                         (value, settings['DATE_FMT']))

    def start_requests(self):
        for parser, urls in self.start_callbacks.items():
            callback = partial(getattr(parsers, parser).parse, self)
            for url in urls:
                yield Request(url, callback)

