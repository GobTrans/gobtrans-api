import re
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from scrapemark import scrape
from scrapy.http import FormRequest
from collections import defaultdict

from scraping.items import SubstitutesItem

get_substitution_range = lambda why: re.findall('([\d/]+)', why, re.UNICODE)
get_substitution_reason = lambda why: re.match('(.*?) desde', why, re.UNICODE).group(1)

def parse(spider, resp):
    return FormRequest(resp.url,
                       formdata={
                           'Fecha': datetime.today().strftime(DATE_FMT),
                           'Cuerpo': resp.url[-1],
                           'Integracion': 'S',
                           'Desde': '15021985',
                           'Hasta': datetime.today().strftime(DATE_FMT),
                           'Dummy': datetime.today().strftime(DATE_FMT),
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
        {* <font>Sustituye al <a>{{ [res].name }}</a>{{ [res].why }}</font>*}
        """,
        html=html)['res']

    items = []
    for info in members:
        since = None
        to = None
        why = None
        substitutes = None
        if 'ref' in info and info['ref'] is not None:
            ref = int(info['ref'])
            sub_info = refs[ref-1]

            substitutes = sub_info['name']
            range = get_substitution_range(sub_info['why'])
            why = get_substitution_reason(sub_info['why'])

            if len(range) > 0:
                since = range[0]
            if len(range) > 1:
                to = range[1]
        items.append(SubstitutesItem(name=info['name'],
                                     party=info['party'], 
                                     chamber=resp.url[-1],
                                     substitutes=substitutes,
                                     substitutes_from=since,
                                     substitutes_to=to,
                                     substitutes_why=why))

    return items
