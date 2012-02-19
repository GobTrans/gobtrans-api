import os

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
        ('http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=S', 'substitutes'),
        ('http://www0.parlamento.gub.uy/forms/IntCpo.asp?Cuerpo=D', 'substitutes'),
        ('http://www0.parlamento.gub.uy/palacio3/abms2/asistsala/ConsAsistenciabrief.asp', 'assistance'),
    )

    def __init__(self, *args, **kwargs):
        super(ParlamentoSpider, self).__init__(*args, **kwargs)
        if kwargs:
            self.start_callbacks = [(url, callback) for url, callback in kwargs.items()]

    def start_requests(self):
        # Here be dragons
        return map(lambda sc: 
                       Request(sc[0], lambda resp: getattr(parsers, sc[1]).parse(self, resp)),
                   self.start_callbacks)
