# Scrapy settings for scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
from os import path
PROJECT_ROOT = path.dirname(__file__)

BOT_NAME = 'GobiernoTransparenteBot'
BOT_VERSION = '1.0'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = SPIDER_MODULES[0]

ITEM_PIPELINES = ['scraping.pipelines.SQLAlchemyPipeline']
SQLALCHEMY_ENGINE_URL = 'sqlite:////path/to/db.sqlite' # redefined in local_settings

RETRY_HTTP_CODES = [500, 503, 504, 400, 408]
RETRY_TIMES = 9

HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = RETRY_HTTP_CODES

CONCURRENT_REQUESTS_PER_DOMAIN = 1

# sensitive and deploy-specific settings (untracked)
local_settings_path = path.join(PROJECT_ROOT, 'local_settings.py')
if path.exists(local_settings_path):
    # use execfile to allow modifications within this context
    execfile(local_settings_path)
