import urlparse
import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

class SimpleSpider(BaseSpider):
    name = "simplespider"
    start_urls = [
       "http://www.eurogamer.net/"
    ]

    def parse_css(self, response):
        matches = re.finditer('@import[^"\']*["\']([^"\']*)', response.body)
        # Download external CSS from a CSS file
        for m in matches:
            rel_url = m.group(1)
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=self.parse_css)
        
        # Download images from CSS
        urls = re.finditer('url\(([^\)]+)\)', response.body)
        ext = ["gif", "jpg", "jpeg", "png", "svg", "ttf", "eot", "off"]
        for m in urls:
            rel_url = m.group(1).strip("'").strip('"')
            if rel_url[-3:].lower() not in ext:
                continue
            abs_url = urlparse.urljoin(response.url, rel_url)
            yield Request(abs_url, callback=lambda _: None)

    # Parses HTML pages for images, CSS, and javascript
    def parse(self, response):
        # Get favicon
        yield Request(urlparse.urljoin(response.url, "/favicon.ico"),
                      callback=lambda _: None)
        
        hxs = HtmlXPathSelector(response)
        image_tags = hxs.select('//img')
        for img in image_tags:
            rel_url = img.select('@src').extract()[0]
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=lambda _: None)

        links = hxs.select('//link[contains(@type,"css")]/@href').extract()
        for link in links:
            yield Request(link, callback=self.parse_css)
            
        scripts = hxs.select('//script/@src').extract()
        for script in scripts:
            if 'recaptcha_ajax.js' in script:
                continue
            yield Request(script, callback=lambda _: None)
