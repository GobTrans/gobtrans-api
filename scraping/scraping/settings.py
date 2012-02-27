# Scrapy settings for scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'GobiernoTransparenteBot'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = 'scraping.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

RETRY_HTTP_CODES = [500, 503, 504, 400, 408]
RETRY_TIMES = 9

HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = RETRY_HTTP_CODES

CONCURRENT_REQUESTS_PER_DOMAIN = 1
