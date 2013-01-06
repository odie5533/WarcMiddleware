import urlparse
import re
import xml.etree.ElementTree

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

class SimpleSpider(BaseSpider):
    name = "simplespider"

    @staticmethod
    def load_sitemap(sitemap):
        tree = xml.etree.ElementTree.parse(sitemap)
        root = tree.getroot()

        found_urls = []
        for url in root:
            if not url.tag.endswith('url'): continue
            for loc in url:
                if not loc.tag.endswith('loc'): continue
                found_urls.append(loc.text)
        return found_urls

    def __init__(self, url=None, sitemap=None):
        self.start_urls = []
        if url is not None:
            self.start_urls.append(url)
        if sitemap is not None:
            urls = self.load_sitemap(sitemap)
            self.start_urls.extend(urls)

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
        image_tags = hxs.select('//img/@src').extract()
        for rel_url in image_tags:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=lambda _: None)

        # Parse CSS
        css_urls = hxs.select('//link[contains(@type,"css")]/@href').extract()
        for rel_url in css_urls:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=self.parse_css)

        # Parse JavaScript
        scripts = hxs.select('//script/@src').extract()
        for rel_url in scripts:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=lambda _: None)
