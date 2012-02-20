from datetime import datetime
from BeautifulSoup import BeautifulSoup
from scrapemark import scrape
from scrapy.http import FormRequest
from collections import defaultdict

from scraping.items import SubstitutesItem

date_fmt = '%d%m%Y'

def parse(spider, resp):
    return FormRequest(resp.url,
                       formdata={
                           'Fecha': datetime.today().strftime(date_fmt),
                           'Cuerpo': resp.url[-1],
                           'Integracion': 'S',
                           'Desde': '15021985',
                           'Hasta': datetime.today().strftime(date_fmt),
                           'Dummy': datetime.today().strftime(date_fmt),
                           'TipoLeg': 'Act',
                           'Orden': 'Legislador',
                       },
                       callback=parse_list)

def parse_list(resp):
    html = BeautifulSoup(resp.body).prettify()

    members = scrape(
        """{* 
            <tr>
                <td>
                    <a>{{ [res].name }}</a>
                    {* <strong>({{ [res].ref }})</strong> *}
                </td>
                <td>
                    <font>partido {{ [res].party }}</font>
                </td>
            </tr>
        *}""",
        html=html)['res']

    refs = scrape(
        """
        {* <font>Sustituye al <a>{{ [res].name }}</a>{{ [res].why }}{* desde el {{ [res].from }}*}{* hasta el {{ [res].to }}*}</font>*}
        """,
        html=html)['res']


    items = []
    for info in members:
        if 'ref' in info and info['ref'] is not None:
            ref = int(info['ref'])
            substitutes = refs[ref-1]
        else:
            substitutes = defaultdict(lambda: None)
        items.append(SubstitutesItem(name=info['name'],
                                     party=info['party'], 
                                     chamber=resp.url[-1],
                                     substitutes=substitutes['name'],
                                     substitutes_from=substitutes['from'],
                                     substitutes_to=substitutes['to'],
                                     substitutes_why=substitutes['why']))

    return items
