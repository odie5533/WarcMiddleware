# Scrapy settings for crawltest project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'crawltest'

SPIDER_MODULES = ['crawltest.spiders']
NEWSPIDER_MODULE = 'crawltest.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawltest (+http://www.yourdomain.com)'

DOWNLOADER_HTTPCLIENTFACTORY = 'warcclientfactory.WarcHTTPClientFactory'

# Use priority 820 to capture the data before Scrapy modifies it
#DOWNLOADER_MIDDLEWARES = {'warcmiddleware.WarcMiddleware': 820}
