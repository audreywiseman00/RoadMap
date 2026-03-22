import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from source import SourceObject

class TestSourceObject(unittest.TestCase):
    
    def test_init_with_all_parameters(self):
        obj = SourceObject(url="https://example.com", title="Example", type="article")
        self.assertEqual(obj.url, "https://example.com")
        self.assertEqual(obj.title, "Example")
        self.assertEqual(obj.type, "article")
        self.assertIsNone(obj.timestamp)
    
    def test_init_with_no_parameters(self):
        obj = SourceObject()
        self.assertIsNone(obj.url)
        self.assertIsNone(obj.title)
        self.assertIsNone(obj.type)
        self.assertIsNone(obj.timestamp)
    
    def test_init_with_partial_parameters(self):
        obj = SourceObject(url="https://example.com", title="Example")
        self.assertEqual(obj.url, "https://example.com")
        self.assertEqual(obj.title, "Example")
        self.assertIsNone(obj.type)
        self.assertIsNone(obj.timestamp)
    
    def test_timestamp_attribute_exists(self):
        obj = SourceObject()
        self.assertTrue(hasattr(obj, 'timestamp'))
    
    def test_set_timestamp(self):
        obj = SourceObject()
        obj.timestamp = "2024-01-01T00:00:00Z"
        self.assertEqual(obj.timestamp, "2024-01-01T00:00:00Z")


if __name__ == '__main__':
    unittest.main()