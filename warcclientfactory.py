from StringIO import StringIO

from scrapy.core.downloader.webclient import ScrapyHTTPPageGetter, ScrapyHTTPClientFactory

import warcrecords

"""
Singleton that handles maintaining a single output file for many connections

"""
class WarcOutputSingleton(object):
    _instance = None

    def __new__(cls, * args, **kwargs):
        if not cls._instance:
            cls._instance = super(WarcOutputSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Make sure init is not called more than once
        try:
            self.__fo
        except AttributeError:
            self.__fo = open('out.warc', 'wb')
            record = warcrecords.WarcinfoRecord()
            record.write_to(self.__fo)
    
    """ Returns a handle to the output file """
    def get_handle(self):
        return self.__fo

"""
Twisted Protocol class that writes the request and response to a WARC file

"""
class WarcHTTPPageGetter(ScrapyHTTPPageGetter):
    def __init__(self, *args, **kwargs):
        self.block_buffer = StringIO()
        self._warcout = WarcOutputSingleton().get_handle()
    
    def lineReceived(self, line):
        # line is missing \n, so strip off the \r and add both back
        self.block_buffer.write(line.rstrip() + '\r\n')
        return ScrapyHTTPPageGetter.lineReceived(self, line.rstrip())
        
    # Called after the entire raw response is received
    def handleResponse(self, response):
        self.block_buffer.write(response)
        self.block_buffer.write('\r\n\r\n')
        
        block_string = self.block_buffer.getvalue()
        record = warcrecords.WarcResponseRecord(url=self.factory.url, block=block_string)
        record.write_to(self._warcout)
        
        ScrapyHTTPPageGetter.handleResponse(self, response)
    
    """
    Handles entire Request saving
    
    """
    def connectionMade(self):
        # Create a fake_transport. Let ScrapyHTTPPageGetter make its request.
        # Then save the request as a WARC record and send it off
        real_transport = self.transport
        fake_transport = StringIO()
        self.transport = fake_transport
        
        ScrapyHTTPPageGetter.connectionMade(self)
        
        self.transport = real_transport
        send_string = fake_transport.getvalue()
        real_transport.write(send_string)
        
        record = warcrecords.WarcRequestRecord(url=self.factory.url, block=send_string)
        record.write_to(self._warcout)

"""
Used to override the factory's protocol to WarcHTTPPageGetter

"""
class WarcHTTPClientFactory(ScrapyHTTPClientFactory):
    def __init__(self, *args, **kwargs):
        self.protocol = WarcHTTPPageGetter
        ScrapyHTTPClientFactory.__init__(self, *args, **kwargs)
