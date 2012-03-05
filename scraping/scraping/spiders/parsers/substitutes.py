import logging
import sys
import re
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from scrapemark import scrape
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.conf import settings
from collections import defaultdict

from scraping.items import SubstitutesItem

logger = logging.getLogger(__name__)

POST_DATE_FMT  = '%d%m%Y'
PAGE_DATE_FMT  = '%d/%m/%Y'
SUBS_DATES_RE  = re.compile('([\d/]+)', re.UNICODE)
SUBS_REASON_RE = re.compile('(.*?) desde', re.UNICODE)
ID_LINK_RE     = re.compile('[iI][dD]=([\d]+)', re.UNICODE)

get_substitution_range = lambda why: SUBS_DATES_RE.findall(why)
get_substitution_reason = lambda why: SUBS_REASON_RE.match(why).group(1)
extract_id_link = lambda idlink: ID_LINK_RE.search(idlink).group(1)

def dates_gen(start, end):
    """ Iterate over days from start to end """
    d = timedelta(days=1)
    while True:
        yield start
        start += d
        if end <= start:
            return

def parse(spider, resp):
    reqs = []
    for date in dates_gen(spider.date_start, spider.date_end):
        date_str = date.strftime(POST_DATE_FMT)
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
        refs[ref] = tr

    items = []
    for info in members:
        since = None
        to = None
        line = None
        substitutes_name = None
        substitutes_oid = None
        if 'ref' in info and info['ref'] is not None:
            try:
                tr = refs[info['ref']]
            except KeyError:
                logger.warning('Couldnt find reference %s in substitutes table.' % \
                               info['ref'], exc_info=sys.exc_info())
            line = "".join(tr.select('.//td[2]/font/descendant-or-self::*/text()').extract())
            links = tr.select('.//a')
            if links:
                substitutes_oid = extract_id_link(links[0].select('.//@href').extract()[0])[2:]
                substitutes_name = links[0].select('.//text()').extract()[0]
            range = get_substitution_range(line)
            if len(range) > 0:
                try:
                    since = datetime.strptime(range[0], PAGE_DATE_FMT).date()
                except ValueError, e:
                    logger.warning("Unable to parse substitute 'since' date", exc_info=sys.exc_info())
            if len(range) > 1:
                try:
                    to = datetime.strptime(range[1], PAGE_DATE_FMT).date()
                except ValueError, e:
                    logger.warning("Unable to parse substitute 'to' date", exc_info=sys.exc_info())

        date = resp.meta['date']
        idlink = extract_id_link(info['idlink'])
        items.append(SubstitutesItem(date=date,
                                     legislature_id=idlink[:2],
                                     original_id=idlink[2:],
                                     name=info['name'],
                                     party=info['party'], 
                                     chamber=resp.url[-1],
                                     substitutes_name=substitutes_name,
                                     substitutes_oid=substitutes_oid,
                                     substitutes_from=since,
                                     substitutes_to=to,
                                     substitutes_line=line))

    return items
