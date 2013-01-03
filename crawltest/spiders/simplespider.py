import urlparse
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from scrapy.item import Item, Field

class SimpleItem(Item):
    image_urls = Field()
    images = Field()

class SimpleSpider(BaseSpider):
    name = "simplespider"
    start_urls = [
       "http://www.pcgamer.com/"
    ]

    def parse_css(self, response):
        matches = re.finditer('@import[^"\']*["\']([^"\']*)', response.body)
        for m in matches:
            rel_url = m.group(1)
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=self.parse_css)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        items = []

        sites = hxs.select('//img')
        for site in sites:
            item = SimpleItem()
            rel_url = site.select('@src').extract()[0]
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            item['image_urls'] = [abs_url]
            yield item

        links = hxs.select('//link[contains(@type,"css")]/@href').extract()
        for link in links:
            yield Request(link, callback=self.parse_css)
            
        scripts = hxs.select('//script/@src').extract()
        for script in scripts:
            yield Request(script)
