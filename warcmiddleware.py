from urlparse import urlparse, urlunparse, urldefrag
from cStringIO import StringIO

import scrapy
from scrapy.http import Headers
from scrapy.utils.httpobj import urlparse_cached
from twisted.web.http import HTTPClient
from warcrecords import WarcinfoRecord, WarcRequestRecord, WarcResponseRecord
        
# from scrapy/core/downloader/webclient.py
def _parsed_url_args(parsed):
    path = urlunparse(('', '', parsed.path or '/', parsed.params, parsed.query, ''))
    host = parsed.hostname
    port = parsed.port
    scheme = parsed.scheme
    netloc = parsed.netloc
    if port is None:
        port = 443 if scheme == 'https' else 80
    return scheme, netloc, host, port, path

class WarcMiddleware(object):
    def __init__(self):
        self.fo = open('out.warc', 'wb')
        record = WarcinfoRecord()
        record.write_to(self.fo)
    
    """
    Converts a Scrapy request to a WarcRequestRecord
    Simulates a fake HTTP Client to recreate the request
    Follows most of the code from scrapy/core/downloader/webclient.py
    
    """
    def warcrec_from_scrapy_request(self, request):
        headers = Headers(request.headers)
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
        fakeclient = HTTPClient()
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
        return WarcRequestRecord(url=request.url, block=request_str)

    def process_request(self, request, spider):
        record = self.warcrec_from_scrapy_request(request)
        record.write_to(self.fo)
        
    def process_response(self, request, response, spider):
        # Everything is OK.
        response_str = "HTTP/1.0 " + str(response.status) + " OK\r\n"
        response_str += response.headers.to_string()
        response_str += "\r\n\r\n"
        response_str += response.body
        response_str += "\r\n\r\n"
                
        record = WarcResponseRecord(url=response.url, block=response_str)
        record.write_to(self.fo)
        return response

if __name__ == '__main__':
    # Short test only detects major errors
    print 'test'
