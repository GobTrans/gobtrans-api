import re, logging
from urlparse import urljoin
from datetime import datetime

from scrapy.http import Request, FormRequest


class ParseAssistance(object):
    def __init__(self, spider):
        self.spider = spider
        self.logger = logging.getLogger('%s:%s' % (spider.name, self.__class__.__name__))

    def parse_treemap(self, response):
        asistsala_re = re.compile(r"window\.open\(\\'(abms2/asistsala/ConsAsistencia\.asp[^']*)\\',")
        urls = (urljoin(response.url, uri) for uri in asistsala_re.findall(response.body))
        return [Request(uri, self.crawl_preform) for uri in urls]

    def crawl_preform(self, response):
        cons_asistencia_re = re.compile(r'href="(ConsAsistenciaBrief\.asp[^"]*)"')
        urls = (urljoin(response.url, uri) for uri in cons_asistencia_re.findall(response.body))
        return [Request(uri, self.prepare_form) for uri in urls]

    def prepare_form(self, response):
        legislature = re.search(r'>Legislatura ([^<]*)<', response.body).group(1)

        daterange_pattern = r'>Rango de asistencias disponibles para el Cuerpo en la Legislatura: (\d{2}/\d{2}/\d{4}) - (\d{2}/\d{2}/\d{4})<'
        daterange = re.findall(daterange_pattern, response.body)[0]
        post_args = {
            'fecDesde': datetime.strptime(daterange[0], '%d/%m/%Y').strftime('%d%m%Y'),
            'fecHasta': datetime.strptime(daterange[1], '%d/%m/%Y').strftime('%d%m%Y'),
        }

        hidden_input_pattern = r'<INPUT TYPE=HIDDEN[^<]* NAME="([^"]+)" VALUE="([^"]+)">'
        post_args.update(
            dict(re.findall(hidden_input_pattern, response.body))
        )

        form_uri_pattern = r'<FORM METHOD=POST ACTION="([^"]+)"'
        form_url = urljoin(response.url, re.search(form_uri_pattern, response.body).group(1))

        callback = lambda response: self.parse_form_result(response, legislature)
        return FormRequest(url=form_url, formdata=post_args, callback=callback)

    def parse_form_result(self, response, legislature=None):
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

