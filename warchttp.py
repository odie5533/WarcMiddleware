from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler, ScrapyAgent
import scrapy.xlib.tx.client
import scrapy.xlib.tx._newclient

class FakeTransport:
    def writeSequence(self, requestLines):
        print "writeSequence", requestLines

class MyRequest(scrapy.xlib.tx._newclient.Request):
    def __init__(self, method, uri, headers, bodyProducer, persistent=False):
        super(MyRequest, self).__init__(method, uri, headers,
                                                bodyProducer, persistent=False)
        ft = FakeTransport()
        self._writeHeaders(ft, None)

class WarcAgent(scrapy.xlib.tx.client.Agent):
    def _requestWithEndpoint(self, key, endpoint, method, parsedURI,
                             headers, bodyProducer, requestPath):
        # Create minimal headers, if necessary:
        if headers is None:
            headers = Headers()
        if not headers.hasHeader('host'):
            #headers = headers.copy() # not supported in twisted <= 11.1, and it doesn't affects us
            headers.addRawHeader(
                'host', self._computeHostValue(parsedURI.scheme, parsedURI.host,
                                               parsedURI.port))

        d = self._pool.getConnection(key, endpoint)
        def cbConnected(proto):
            return proto.request(
                MyRequest(method, requestPath, headers, bodyProducer,
                        persistent=self._pool.persistent))
        d.addCallback(cbConnected)
        return d

class WarcScrapyAgent(ScrapyAgent):
    _Agent = WarcAgent

class WarcHTTPDownloadHandler(HTTP11DownloadHandler):
    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        agent = WarcScrapyAgent(contextFactory=self._contextFactory, pool=self._pool)
        return agent.download_request(request)
