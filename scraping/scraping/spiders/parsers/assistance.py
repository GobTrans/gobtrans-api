import re, logging
from urlparse import urljoin, parse_qs
from datetime import datetime

from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector

from scraping.items import AssistanceItem


class ParseAssistance(object):
    def __init__(self, spider):
        self.spider = spider
        self.logger = logging.getLogger('%s:%s' % (spider.name, self.__class__.__name__))

    def parse_treemap(self, response):
        asistsala_re = re.compile(r"window\.open\(\\'(abms2/asistsala/ConsAsistencia\.asp[^']*)\\',")
        urls = (urljoin(response.url, uri) for uri in asistsala_re.findall(response.body))
        return [Request(url, self.crawl_preform) for url in urls]

    def crawl_preform(self, response):
        cons_asistencia_re = re.compile(r'href="(ConsAsistenciaBrief\.asp[^"]*)"')
        urls = (urljoin(response.url, uri) for uri in cons_asistencia_re.findall(response.body))
        return [Request(uri, self.prepare_form) for uri in urls]

    def prepare_form(self, response):
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

        return FormRequest(url=form_url, formdata=post_args, callback=self.parse_form_result)

    def parse_form_result(self, response):
        qs = parse_qs(response.request.body)
        legislature, chamber = int(qs['Legislatura'][0]), qs['Cuerpo'][0]

        hxs = HtmlXPathSelector(response)

        a_selector = '//center/a'
        table_selector = '//center/a/following-sibling::table'
        script_selector = '//script[contains(text(), "innerHTML = \'Procesando Sesiones")]'

        z = (hxs.select(selector) for selector in (a_selector, table_selector, script_selector))
        for a, table, script in zip(*z):
            session, session_date = script.select('text()').re('(\d+) del (\d{2}/\d{2}/\d{4})')
            session, session_date = int(session), datetime.strptime(session_date, '%d/%m/%Y').date().isoformat()

            session_diary = a.select('@href').extract()
            session_diary = urljoin(response.url, session_diary[0])
            if session_diary.startswith('javascript:'):
                session_diary = None

            textnodes = table.select('tr/td/div').extract()[0].replace('<br>', '\n').splitlines()

            notes_dict, notes_re = {}, re.compile('<b>\((\d+)\)</b> (.*)')
            for textnode in textnodes:
                match = notes_re.match(textnode)
                if match:
                    notes_dict[match.group(1)] = match.group(2)

            for textnode in textnodes:
                search = (
                    ('present',  u'Asisten los se\xf1ores (?:Senadores|Representantes): (.*)\.'),
                    ('warned',   u'Faltan? con aviso: (.*)\.'),
                    ('unwarned', u'Faltan? sin aviso: (.*)\.'),
                    ('license',  u'Con licencia: (.*)\.'),
                )

                for status, pattern in search:
                    match = re.search(pattern, textnode)
                    if match:
                        asistees = match.group(1).split(',')

                        last = asistees.pop()

                        # first_name last_name
                        # first_name last_name y last_name2

                        # first_name last_name y first_name' last_name'
                        # first_name last_name y first_name' last_name' y last_name2'

                        # first_name last_name y last_name2 y first_name' last_name'
                        # first_name last_name y last_name2 y first_name' last_name' y last_name2'

                        last_chunks = [chunk.split() for chunk in last.split(' y ')]
                        while last_chunks:
                            last_pair = last_chunks[-2:]
                            del last_chunks[-2:]

                            if len(last_pair) == 1:
                                asistees.append(' '.join(last_pair[0]))
                            elif len(last_pair[1]) == 1:
                                asistees.append(' y '.join(' '.join(chunk) for chunk in last_pair))
                            else:
                                asistees.append(' '.join(last_pair[1]))
                                last_chunks.append(last_pair[0])

                        for asistee in (asistee.strip() for asistee in asistees):
                            notes, notes_re = None, re.compile(' <b>\((\d+)\)</b>')
                            if notes_re.search(asistee):
                                notes = [notes_dict[note_n] for note_n in notes_re.findall(asistee)]
                                asistee = notes_re.sub('', asistee)

                            yield AssistanceItem(
                                legislature   = legislature,
                                chamber       = chamber,
                                session       = session,
                                session_date  = session_date,
                                session_diary = session_diary,
                                asistee       = asistee,
                                status        = status,
                                notes         = notes,
                            )


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

