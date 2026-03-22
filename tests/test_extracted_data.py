import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from extracted_data import ExtractedData

class TestExtractedData(unittest.TestCase):

    def setUp(self):
        self.data = ExtractedData()
        self.data_with_values = ExtractedData(
            source="test_source",
            locations=["New York", "London"],
            orgs=["Company A", "Company B"],
            activities=["Activity 1"],
            signals=["Signal 1"],
            context=["Context 1"]
        )

    def test_init_default_values(self):
        self.assertIsNone(self.data.source)
        self.assertEqual(self.data.locations, [])
        self.assertEqual(self.data.orgs, [])
        self.assertEqual(self.data.activities, [])
        self.assertEqual(self.data.signals, [])
        self.assertEqual(self.data.context, [])
        self.assertIsNone(self.data.confidence)

    def test_init_with_values(self):
        self.assertEqual(self.data_with_values.source, "test_source")
        self.assertEqual(self.data_with_values.locations, ["New York", "London"])
        self.assertEqual(self.data_with_values.orgs, ["Company A", "Company B"])

    def test_get_source(self):
        self.assertEqual(self.data_with_values.get_source(), "test_source")
        self.assertIsNone(self.data.get_source())

    def test_get_locations(self):
        self.assertEqual(self.data_with_values.get_locations(), ["New York", "London"])
        self.assertEqual(self.data.get_locations(), [])

    def test_get_activities(self):
        self.assertEqual(self.data_with_values.get_activities(), ["Activity 1"])
        self.assertEqual(self.data.get_activities(), [])

    def test_get_signals(self):
        self.assertEqual(self.data_with_values.get_signals(), ["Signal 1"])
        self.assertEqual(self.data.get_signals(), [])


if __name__ == '__main__':
    unittest.main()