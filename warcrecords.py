import hashlib, uuid, base64
import datetime

from hanzo.warctools import WarcRecord

# Adds a new method called make_warc_uuid to the WarcRecord class
@staticmethod
def make_warc_uuid(text=None):
    if text is None:
        text = str(datetime.datetime.utcnow())
    return "<urn:uuid:%s>"%uuid.UUID(hashlib.sha1(text).hexdigest()[0:32])
WarcRecord.make_warc_uuid = make_warc_uuid

# Overrides the block_digest method in WarcRecord to output base32 sha1
def block_digest(self, content_buffer):
    hash = base64.b32encode(hashlib.sha1(content_buffer).digest())
    return "sha1:%s" % hash
WarcRecord.block_digest = block_digest

"""
Container to handle application/warc-fields as part of a warcinfo record

"""
class WarcinfoFields:
    _common_fields = ['software','format','conformsTo','robots','operator',
                       'hostname','ip','http-header-user-agent',
                       'http-header-from']
    CONFORMS_TO = 'http://bibnum.bnf.fr/WARC/WARC_ISO_28500_version1_latestdraft.pdf'
    def __init__(self, fields=None, defaults=True, **kwargs):
        if fields is None:
            self._fields = []
        else:
            self._fields = fields
        
        # Copy common field arguments to self.fields
        # Fields are copied in the order they appear in common_fields
        for field in self._common_fields:
            if field in kwargs:
                self._fields.append((field, kwargs[field]))
        if defaults:
            if not self.has_field('software'):
                self._fields.append(('software', 'Python'))
            if not self.has_field('format'):
                self._fields.append(('format', 'WARC File Format 1.0'))
            if not self.has_field('conformsTo'):
                self._fields.append(('conformsTo', self.CONFORMS_TO))
            if not self.has_field('robots'):
                self._fields.append(('robots', 'classic'))
                
    """
    Append custom fields to the container
    
    """
    def append(self, tuple):
        self._fields.append(tuple)
    
    """
    Check if the container has a field
    
    """
    def has_field(self, key):
        for (k,v) in self._fields:
            if k.lower() == key.lower():
                return True
        return False

    """
    Retrieve the first value of a field for a given key
    
    """
    def get_field(self, key):
        for (k,v) in self._fields:
            if k.lower() == key.lower():
                return v
        return None
    """
    Set the first value of a field for a given key
    Creates the key if it does not exist
    
    """
    def set_field(self, key, value=None):
        # accepts tuples of (key, value)
        if value is None:
            key,value = key
        for n,i in enumerate(self._fields):
            k,v = i
            if k.lower() == key.lower():
                self._fields[n] = (key, value)
                return
        self.append((key, value))

    """
    Magic functions are used to imitate a tuple
    
    """
    def __str__(self):
        return '\r\n'.join(k+': '+v for (k,v) in self._fields) + '\r\n\r\n'
    def __getitem__(self, key):
        if key == 0:
            return 'application/warc-fields'
        elif key == 1:
            str(self)
    def __len__(self):
        return len(self._fields)
    def __iter__(self):
        for i in ['application/warc-fields', str(self)]:
            yield i

"""
Handles warcinfo records. These are the header at the top of a WARC file and
they often include application/warc-fields content in the block.

"""
class WarcinfoRecord(WarcRecord):
    def __init__(self, id=None, date=None, filename=None, content=None,
                 headers=None, defaults=True):
        if headers is None:
            headers = []
        headers.append((WarcRecord.TYPE, WarcRecord.WARCINFO))
        
        if id:
            headers.append((WarcRecord.ID, id))
        elif defaults:
            headers.append((WarcRecord.ID, self.make_warc_uuid()))
        if date:
            headers.append((WarcRecord.DATE, date))
        elif defaults:
            date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            headers.append((WarcRecord.DATE, date))
        if filename:
            headers.append((WarcRecord.FILENAME, filename))

        # content is expected to behave like a tuple
        # (iterable and valid in truth testing)
        # WarcinfoFields uses magic functions to imitate a tuple
        if not content and defaults:
            content = WarcinfoFields(defaults=defaults)
        super(WarcinfoRecord, self).__init__(headers=headers, content=content)

class WarcRequestRecord(WarcRecord):
    def __init__(self, id=None, date=None, url=None, block=None,
                 concurrent_to=None, headers=None, defaults=True):
        assert block is not None
        if headers is None:
            headers = []
        headers.append((WarcRecord.TYPE, WarcRecord.REQUEST))
        if id:
            headers.append((WarcRecord.ID, id))
        elif defaults:
            headers.append((WarcRecord.ID, self.make_warc_uuid()))
        if date:
            headers.append((WarcRecord.DATE, date))
        elif defaults:
            date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            headers.append((WarcRecord.DATE, date))
        if url:
            headers.append((WarcRecord.URL, url))
        if concurrent_to:
            headers.append((WarcRecord.CONCURRENT_TO, concurrent_to))

        content = ('application/http;msgtype=request', block)
        super(WarcRequestRecord, self).__init__(headers=headers, content=content)

class WarcResponseRecord(WarcRecord):
    def __init__(self, id=None, date=None, url=None, block=None,
                 concurrent_to=None, headers=None, defaults=True):
        assert block is not None
        if headers is None:
            headers = []
        headers.append((WarcRecord.TYPE, WarcRecord.RESPONSE))
        if id:
            headers.append((WarcRecord.ID, id))
        elif defaults:
            headers.append((WarcRecord.ID, self.make_warc_uuid()))
        if date:
            headers.append((WarcRecord.DATE, date))
        elif defaults:
            date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            headers.append((WarcRecord.DATE, date))
        if url:
            headers.append((WarcRecord.URL, url))
        if concurrent_to:
            headers.append((WarcRecord.CONCURRENT_TO, concurrent_to))

        content = ('application/http;msgtype=response', block)
        super(WarcResponseRecord, self).__init__(headers=headers, content=content)
