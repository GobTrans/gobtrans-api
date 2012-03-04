# -*- coding: utf-8 -*-
# Scrapy settings for scraping project
# http://doc.scrapy.org/topics/settings.html
from os import path
import datetime

PROJECT_ROOT = path.dirname(path.abspath(__file__))

BOT_NAME = 'GobiernoTransparenteBot'
BOT_VERSION = '1.0'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = SPIDER_MODULES[0]

ITEM_PIPELINES = ['scraping.pipelines.SQLAlchemyPipeline']

RETRY_HTTP_CODES = [500, 503, 504, 400, 408]
RETRY_TIMES = 9

HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = RETRY_HTTP_CODES

CONCURRENT_REQUESTS_PER_DOMAIN = 1

DATE_FMT='%Y-%m-%d'

# The following directives should be redefined in localsettings.py

SCRAPER_DATE_START='1985-02-15'

SCRAPER_DATE_END=datetime.date.today()

# Include localsettings.py
local_settings_path = path.join(PROJECT_ROOT, 'localsettings.py')
if path.exists(local_settings_path):
    # use execfile to allow modifications within this context
    execfile(local_settings_path)
else:
    import sys
    sys.stderr.write("Can't find local settings, using default settings.\n")
