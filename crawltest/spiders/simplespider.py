import urlparse
import re
import xml.etree.ElementTree

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log

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

    @staticmethod
    def urls_from_file(filename):
        f = open(filename, 'r')
        urls = [l.strip() for l in f]
        f.close()
        return urls

    def __init__(self, urls=None, sitemap=None, mirror=None, reg_accept=None,
                 reg_reject=None, domains=None, url_file=None):
        self.start_urls = []
        self.accept_netlocs = [] # By default, do not crawl links
        self.regs_accept = None
        self.regs_reject = None

        if urls is not None:
            urls = urls.split(',')
            self.start_urls.extend(urls)
        if url_file is not None:
            self.start_urls.extend(self.urls_from_file(url_file))
        if sitemap is not None:
            self.log("Sitemap crawl: %s" % sitemap, log.DEBUG)
            urls = self.load_sitemap(sitemap)
            self.start_urls.extend(urls)
        if reg_accept is not None:
            regs = reg_accept.split(',')
            self.regs_accept = [re.compile(reg) for reg in regs]
            self.accept_netlocs = None
                             # Setting accept_netlocs to None tells it to crawl
                             # accept any domain and links based on regexp
                             # unless domains or mirros is specified to override
        if reg_reject is not None:
            regs = reg_reject.split(',')
            self.regs_reject = [re.compile(reg) for reg in regs]
        if mirror is not None:
            parts = urlparse.urlparse(urls[0])
            self.accept_netlocs = [parts.netloc.lower()]
        # domains overrides mirror
        if domains is not None:
            domains = domains.split(',')
            self.accept_netlocs = domains

        if self.accept_netlocs:
            self.accept_netlocs = [n.lower() for n in self.accept_netlocs]
            self.log("Using accept_netlocs: %s" %self.accept_netlocs, log.DEBUG)
        if len(self.start_urls) > 5:
            self.log("Crawling many urls: %d" % len(self.start_urls), log.DEBUG)
        else:
            self.log("Crawling start_urls: %s" % self.start_urls, log.DEBUG)

    """
    Pure function that applies a set of rules to a url to determine if it should
    be crawled. Returns True if it should be crawled.

    """
    @staticmethod
    def crawl_ruled(url, accept_netlocs=None, regs_accept=None,
                    regs_reject=None):
        # If None is supplied to netlocs, ignore accept_netlocs
        # If an empty list [] is supplied, returns False
        if accept_netlocs is not None:
            parts = urlparse.urlparse(url)
            if parts.netloc.lower() not in accept_netlocs:
                return False

        if regs_accept is not None:
            accept = False
            for comp in regs_accept:
                if comp.search(url):
                    accept = True
            if accept is False:
                return False

        if regs_reject is not None:
            accept = True
            for comp in regs_reject:
                if comp.search(url):
                    accept = False
            if accept is False:
                return False

        return True

    """
    Crawls a response containing a CSS file

    """
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

    """
    Crawls content in a response

    """
    def parse(self, response):
        # Do not parse these mime types
        skip_types = ['application/pdf', 'image/png', 'image/gif', 'image/jpeg']
        if 'Content-Type' in response.headers:
            if response.headers['Content-Type'] in skip_types:
                return
            if response.headers['Content-Type'].startswith("text/javascript"):
                return
        # Get favicon
        yield Request(urlparse.urljoin(response.url, "/favicon.ico"),
                      callback=lambda _: None)

        hxs = HtmlXPathSelector(response)

        # Parses anchor tags to find links to crawl
        anchors = hxs.select('//a/@href').extract()
        for rel_url in anchors:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            if self.crawl_ruled(abs_url,
                                accept_netlocs=self.accept_netlocs,
                                regs_accept=self.regs_accept,
                                regs_reject=self.regs_reject):
                yield Request(abs_url)

        # Parses for images
        image_tags = hxs.select('//img/@src').extract()
        for rel_url in image_tags:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=lambda _: None)

        # Parses for CSS
        css_urls = hxs.select('//link[contains(@type,"css")]/@href').extract()
        for rel_url in css_urls:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=self.parse_css)

        # Parses for JavaScript
        scripts = hxs.select('//script/@src').extract()
        for rel_url in scripts:
            abs_url = urlparse.urljoin(response.url, rel_url.strip())
            yield Request(abs_url, callback=lambda _: None)
