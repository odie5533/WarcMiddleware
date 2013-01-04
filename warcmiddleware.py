import urlparse
from cStringIO import StringIO

import scrapy.http
import twisted.web.http
from scrapy.utils.httpobj import urlparse_cached

import warcrecords

# from scrapy/core/downloader/webclient.py
def _parsed_url_args(parsed):
    path = urlparse.urlunparse(('', '', parsed.path or '/', parsed.params,
                                parsed.query, ''))
    host = parsed.hostname
    port = parsed.port
    scheme = parsed.scheme
    netloc = parsed.netloc
    if port is None:
        port = 443 if scheme == 'https' else 80
    return scheme, netloc, host, port, path

class WarcMiddleware(object):
    """
    Open the WARC file for output and write the warcinfo header record
    
    """
    def __init__(self):
        self.fo = open('out.warc', 'wb')
        record = warcrecords.WarcinfoRecord()
        record.write_to(self.fo)

    """
    Converts a Scrapy request to a WarcRequestRecord
    Simulates a fake HTTP Client to recreate the request
    Follows most of the code from scrapy/core/downloader/webclient.py
    
    """
    def warcrec_from_scrapy_request(self, request):
        headers = scrapy.http.Headers(request.headers)
        body = request.body

        parsed = urlparse_cached(request)
        scheme, netloc, host, port, path = _parsed_url_args(parsed)

        # set Host header based on url
        headers.setdefault('Host', netloc)

        # set Content-Length based len of body
        if body is not None:
            headers['Content-Length'] = len(body)
            # just in case a broken http/1.1 decides to keep connection alive
            headers.setdefault("Connection", "close")

        string_transport = StringIO()
        fakeclient = twisted.web.http.HTTPClient()
        fakeclient.transport = string_transport
        fakeclient.sendCommand(request.method, path)
        for key, values in headers.items():
            for value in values:
                fakeclient.sendHeader(key, value)
        fakeclient.endHeaders()
        # Body
        if body is not None:
            string_transport.write(body)

        request_str = string_transport.getvalue()
        return warcrecords.WarcRequestRecord(url=request.url, block=request_str)

    """
    Converts a Scrapy response to a WarcResponseRecord
    
    tofix: Handle response.status codes
    
    """
    def warcrec_from_scrapy_response(self, response):
        # Everything is OK.
        resp_str = "HTTP/1.0 " + str(response.status) + " OK\r\n"
        resp_str += response.headers.to_string()
        resp_str += "\r\n\r\n"
        resp_str += response.body
        resp_str += "\r\n\r\n"

        return warcrecords.WarcResponseRecord(url=response.url, block=resp_str)

    def process_request(self, request, spider):
        record = self.warcrec_from_scrapy_request(request)
        record.write_to(self.fo)

    def process_response(self, request, response, spider):
        record = self.warcrec_from_scrapy_response(response)
        record.write_to(self.fo)
        return response # return the response to Scrapy for further handling
