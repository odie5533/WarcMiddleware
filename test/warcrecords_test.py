import unittest
from StringIO import StringIO

from warcrecords import WarcinfoRecord
from hanzo.warctools import WarcRecord

def record_to_string(record):
    buffer = StringIO()
    record.write_to(buffer)
    return buffer.getvalue()

class TestWarcinfoRecord(unittest.TestCase):
    def id_test(self, defaults):
        info = WarcinfoRecord(id="test", defaults=defaults)
        self.assertEqual(info.get_header(WarcRecord.ID), "test")
        
        string = record_to_string(info)
        self.assertIn("WARC-Record-ID: test", string)
        
    def test_id(self):
        self.id_test(defaults=True)
        self.id_test(defaults=False)
        
    def date_test(self, defaults):
        info = WarcinfoRecord(date="test", defaults=defaults)
        self.assertEqual(info.get_header("WARC-Date"), "test")
        
        string = record_to_string(info)
        self.assertIn("WARC-Date: test", string)

    def test_date(self):
        self.date_test(defaults=True)
        self.date_test(defaults=False)
        
    def test_filename(self):
        info = WarcinfoRecord(filename="test")
        self.assertEqual(info.get_header("WARC-Filename"), "test")
        
        string = record_to_string(info)
        self.assertIn("WARC-Filename: test", string)

    def test_type(self):
        info = WarcinfoRecord()
        self.assertEqual(info.get_header(WarcRecord.TYPE), "warcinfo")
        
    def test_defaults(self):
        info = WarcinfoRecord()
        self.assertIsNotNone(info.get_header("WARC-Type"))
        self.assertIsNotNone(info.get_header("WARC-Record-ID"))
        self.assertIsNotNone(info.get_header("WARC-Date"))

    def test_defaults_dump(self):
        info = WarcinfoRecord()
        string = record_to_string(info)
        self.assertEqual("WARC/1.0", string[:8])
        self.assertIn("WARC-Type: ", string)
        self.assertIn("WARC-Record-ID: ", string)
        self.assertIn("WARC-Date: ", string)
        self.assertIn("Content-Type: application/warc-fields", string)
        self.assertIn("Content-Length: ", string)
        self.assertIn("WARC-Block-Digest: ", string)

    def test_sample_data(self):
        headers = [("k1", "v1")]
        info = WarcinfoRecord(id="myid", date="mydate", filename="myfilename",
                              content=("mytype","mycontent"), headers=headers)
        string = record_to_string(info)
        
        self.assertEqual("WARC/1.0", string[:8])
        self.assertIn("WARC-Type: warcinfo", string)
        self.assertIn("WARC-Record-ID: myid", string)
        self.assertIn("WARC-Date: mydate", string)
        self.assertIn("WARC-Filename: myfilename", string)
        self.assertIn("Content-Type: mytype", string)
        self.assertIn("Content-Length: 9", string)
        self.assertIn("WARC-Block-Digest: sha1:2MKCNB7EJF4I7VPZPJVUNHBIJ5S37ASD", string)
        self.assertEqual("\r\n\r\nmycontent\r\n\r\n", string [-17:])
