import re, logging
from urlparse import urljoin

from scrapy.http import Request


class ParseAssistance(object):
    def __init__(self, spider):
        self.spider = spider
        self.logger = logging.getLogger('%s:%s' % (spider.name, self.__class__.__name__))

    def parse_treemap(self, response):
        asistsala_re = re.compile(r"window\.open\(\\'(abms2/asistsala/ConsAsistencia\.asp[^']*)\\',")
        urls = (urljoin(response.url, uri) for uri in asistsala_re.findall(response.body))
        return (Request(uri, self.crawl_preform) for uri in urls)

    def crawl_preform(self, response):
        cons_asistencia_re = re.compile(r'href="(ConsAsistenciaBrief\.asp[^"]*)"')
        urls = (urljoin(response.url, uri) for uri in cons_asistencia_re.findall(response.body))
        return (Request(uri, self.prepare_form) for uri in urls)

    def prepare_form(self, response):
        pass


def parse(spider, response):
    parser = ParseAssistance(spider)
    return parser.parse_treemap(response)


## senadores 2005/2010
#res = Net::HTTP.post_form(uri,
#                          'FecDesde' => '15022005',
#                          'FecHasta' => '04022010',
#                          'Cuerpo' => 'S',
#                          'Ini' => '15022005',
#                          'Fin' => '04022010',
#                          'Legislatura' => '46',
#                          'Fechas' => 'Seleccionado',
#                          'IMAGE1' => 'Confirmar')
#datos[:senadores] << parse_results(res)
#
## senadores 2010/2015
#res = Net::HTTP.post_form(uri,
#                          'Cuerpo' => 'S',
#                          'FecDesde' => '15022010',
#                          'FecHasta' => '30112011',
#                          'Fechas' => 'Seleccionado',
#                          'Fin' => '30112011',
#                          'IMAGE1' => 'Confirmar',
#                          'Ini' => '15022010',
#                          'Legislatura' => '47')
#datos[:senadores] << parse_results(res)
#
## representantes 2000/2005
#res = Net::HTTP.post_form(uri,
#                          'FecDesde' => '12122001',
#                          'FecHasta' => '15122004',
#                          'Cuerpo' => 'D',
#                          'Ini' => '12122001',
#                          'Fin' => '15122004',
#                          'Legislatura' => '45',
#                          'Fechas' => 'Seleccionado',
#                          'IMAGE1' => 'Confirmar')
#datos[:representantes] << parse_results(res)
#
## representantes 2005/2010
#res = Net::HTTP.post_form(uri,
#                          'FecDesde' => '15022005',
#                          'FecHasta' => '03022010',
#                          'Cuerpo' => 'D',
#                          'Ini' => '15022005',
#                          'Fin' => '03022010',
#                          'Legislatura' => '46',
#                          'Fechas' => 'Seleccionado',
#                          'IMAGE1' => 'Confirmar')
#datos[:representantes] << parse_results(res)
#
## representantes 2010/2015
#res = Net::HTTP.post_form(uri,
#                          'FecDesde' => '15022010',
#                          'FecHasta' => '23102011',
#                          'Cuerpo' => 'D',
#                          'Ini' => '15022010',
#                          'Fin' => '23102011',
#                          'Legislatura' => '47',
#                          'Fechas' => 'Seleccionado',
#                          'IMAGE1' => 'Confirmar')
#datos[:representantes] << parse_results(res)

