# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from scrapemark import scrape
from scrapy.http import Request, FormRequest
from urllib import urlencode
import re
import urlparse


def parse_legislator(resp):
    legislator = {}
    for param in urlparse.parse_qsl(resp.url[resp.url.rfind('?') + 1:]):
        legislator[param[0]] = param[1]
    fot_re = re.compile(r'(/htmlstat/pl/legisl/fotos/Fot\d+\.jpg)')
    matches = fot_re.findall(resp.body)
    if matches:
        matches = 'http://www0.parlamento.gub.uy%s' % matches[0]
        print matches
    legislator['photo'] = matches
    # legislator['name']
    # legislator['party']


def parse_legislature(resp):
    legs = re.compile(r'legisladores/legislador\.asp\?[iI][dD]=(\d+)')
    urls = []
    legislature = resp.url[resp.url.rfind('=') + 1:]
    for legislator in set(legs.findall(resp.body)):
        params = 'legisladores/legislador.asp?%s' % urlencode(
            {'id': legislator,
             'legislatura': legislature})
        req_url = '/'.join((resp.url[:resp.url.rfind('/')], params))
        urls.append(Request(req_url, callback=parse_legislator))
    return urls


def parse(spider, resp):
    legs = re.compile(r'p_legisladores\.asp\?Legislatura=(\d+)')
    urls = []
    for leg_id in set(legs.findall(resp.body)):
        legislature = 'legisladores_der.asp?Legislatura=%s' % leg_id
        req_url = '/'.join((resp.url[:resp.url.rfind('/')], legislature))
        params = {'Deptos': 'TODOS'}
        urls.append(FormRequest(req_url, formdata=params,
                                callback=parse_legislature))
    return urls
