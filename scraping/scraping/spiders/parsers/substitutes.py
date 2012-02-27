import re
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from scrapemark import scrape
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from collections import defaultdict

from scraping.items import SubstitutesItem

DATE_FMT = '%d%m%Y'

SUBS_DATES_RE = re.compile('([\d/]+)', re.UNICODE)
SUBS_REASON_RE = re.compile('(.*?) desde', re.UNICODE)
ID_LINK_RE = re.compile('[iI][dD]=([\d]+)', re.UNICODE)

get_substitution_range = lambda why: SUBS_DATES_RE.findall(why)
get_substitution_reason = lambda why: SUBS_REASON_RE.match(why).group(1)
extract_id_link = lambda idlink: ID_LINK_RE.search(idlink).group(1)

def dates_gen(start):
    """ Iterate over days backwards from today to 15/2/1985 """
    d = timedelta(days=1)
    while True:
        yield start
        start -= d
        if start.year == 1985 and start.month == 2 and start.day == 15:
            return

def parse(spider, resp):
    reqs = []
    for date in dates_gen(datetime.today()):
        date_str = date.strftime(DATE_FMT)
        req = FormRequest(resp.url,
                          formdata={
                              'Fecha': date_str,
                              'Cuerpo': resp.url[-1],
                              'Integracion': 'S',
                              'Desde': '15021985',
                              'Hasta': date_str,
                              'Dummy': date_str,
                              'TipoLeg': 'Act',
                              'Orden': 'Legislador',
                          },
                          callback=parse_list)
        req.meta['date'] = date
        reqs.append(req)
    return reqs

def parse_list(resp):
    html = BeautifulSoup(resp.body).prettify()

    members = scrape(
        """{* 
            <tr>
                <td>
                    <a href='{{ [res].idlink }}'>{{ [res].name }}</a>
                    {* <strong>({{ [res].ref }})</strong> *}
                </td>
                <td>
                    <font>partido {{ [res].party }}</font>
                </td>
            </tr>
        *}""",
        html=html)['res']

    # TODO: The president of the chamber may appear only in a footer. Add him
    #       to the members list.

    sel = HtmlXPathSelector(resp)
    trs = sel.select('//tr/td[@align="RIGHT" and @valign="TOP" and @width="5%"]/font/strong/../../..')
    refs = {}
    for tr in trs:
        ref = tr.select('.//strong[starts-with(text(), "(")]/text()')[0].extract()[1:-1]
        sub_info = "".join(tr.select('.//td[2]/font/descendant-or-self::*/text()').extract())
        refs[ref] = sub_info

    items = []
    for info in members:
        #since = None
        #to = None
        why = None
        #substitutes = None
        if 'ref' in info and info['ref'] is not None:
            why = refs[info['ref']]

            #substitutes = sub_info['name']
            #range = get_substitution_range(sub_info['why'])
            #why = get_substitution_reason(sub_info['why'])

            #if len(range) > 0:
            #    since = range[0]
            #if len(range) > 1:
            #    to = range[1]

        date = resp.meta['date']
        id = extract_id_link(info['idlink']) + date.strftime(DATE_FMT)
        items.append(SubstitutesItem(id=id,
                                     date=date,
                                     name=info['name'],
                                     party=info['party'], 
                                     chamber=resp.url[-1],
                                     #substitutes=substitutes,
                                     #substitutes_from=since,
                                     #substitutes_to=to,
                                     substitutes_line=why))

    return items
