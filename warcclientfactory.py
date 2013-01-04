from StringIO import StringIO

from scrapy.core.downloader.webclient import ScrapyHTTPPageGetter, ScrapyHTTPClientFactory

import warcrecords

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

class WarcHTTPPageGetter(ScrapyHTTPPageGetter):
    def __init__(self, *args, **kwargs):
        self.header_buffer = StringIO()
    
    def lineReceived(self, line):
        self.header_buffer.write(line.rstrip() + '\r\n')
        return ScrapyHTTPPageGetter.lineReceived(self, line.rstrip())
        
    def handleEndHeaders(self):
        self.factory.gotHeaderString(self.header_buffer.getvalue())
        self.factory.gotHeaders(self.headers)
    
    """ Handles entire Request saving """
    def connectionMade(self):
        real_transport = self.transport
        fake_transport = StringIO()
        self.transport = fake_transport
        
        ScrapyHTTPPageGetter.connectionMade(self)
        
        self.transport = real_transport
        send_string = fake_transport.getvalue()
        real_transport.write(send_string)
        
        warcout = WarcOutputSingleton().get_handle()
        record = warcrecords.WarcRequestRecord(url=self.factory.url, block=send_string)
        record.write_to(warcout)

class WarcHTTPClientFactory(ScrapyHTTPClientFactory):
    def gotHeaderString(self, header_string):
        self.block_buffer.write(header_string)

    def page(self, response):
        self.block_buffer.write(response)
        self.block_buffer.write('\r\n\r\n')
        block_string = self.block_buffer.getvalue()
        record = warcrecords.WarcResponseRecord(url=self.url, block=block_string)
        record.write_to(self._warcout)
    
        ScrapyHTTPClientFactory.page(self, response)

    def __init__(self, *args, **kwargs):
        self.protocol = WarcHTTPPageGetter
        
        self._warcout = WarcOutputSingleton().get_handle()
        self.block_buffer = StringIO()
        
        ScrapyHTTPClientFactory.__init__(self, *args, **kwargs)
