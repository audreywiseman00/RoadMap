import unittest
from parser.models import (
    ExtractedData,
    LocationMention,
    SourceObject,
    TravelSignals,
)

class TestExtractedData(unittest.TestCase):

    def setUp(self):
        self.data = ExtractedData()
        self.data_with_values = ExtractedData(
            source=SourceObject(title="Test source"),
            locations=[
                LocationMention("New York", "GPE"),
                LocationMention("London", "GPE"),
            ],
            orgs=["Company A", "Company B"],
            activities=["Activity 1"],
            signals=TravelSignals(price=["Signal 1"])
        )

    def test_init_default_values(self):
        self.assertIsNone(self.data.source)
        self.assertEqual(self.data.locations, [])
        self.assertEqual(self.data.orgs, [])
        self.assertEqual(self.data.activities, [])
        self.assertEqual(self.data.signals, TravelSignals())
        self.assertIsNotNone(self.data.confidence)
        self.assertTrue(self.data.confidence.needs_user_clarification)
        self.assertEqual(self.data.confidence.clarification_reason, "No locations detected")

    def test_init_with_values(self):
        self.assertEqual(self.data_with_values.source.title, "Test source")
        self.assertEqual([loc.name for loc in self.data_with_values.locations], ["New York", "London"])
        self.assertEqual(self.data_with_values.orgs, ["Company A", "Company B"])
        self.assertTrue(self.data_with_values.confidence.needs_user_clarification)
        self.assertFalse(self.data_with_values.confidence.primary_destination_clear)
        self.assertEqual(
            self.data_with_values.confidence.clarification_reason,
            "Multiple locations detected with no clear primary destination",
        )

    def test_single_location_is_marked_as_clear(self):
        data = ExtractedData(locations=[LocationMention("Paris", "GPE")])

        self.assertTrue(data.confidence.primary_destination_clear)
        self.assertFalse(data.confidence.needs_user_clarification)

    def test_unique_frequency_leader_is_marked_as_primary(self):
        data = ExtractedData(locations=[
            LocationMention("Tokyo", "GPE", frequency=3),
            LocationMention("Kyoto", "GPE", frequency=2),
        ])

        self.assertTrue(data.confidence.primary_destination_clear)
        self.assertFalse(data.confidence.needs_user_clarification)

    def test_tied_frequency_leaders_require_clarification(self):
        data = ExtractedData(locations=[
            LocationMention("Tokyo", "GPE", frequency=3),
            LocationMention("Kyoto", "GPE", frequency=3),
            LocationMention("Osaka", "GPE", frequency=1),
        ])

        self.assertFalse(data.confidence.primary_destination_clear)
        self.assertTrue(data.confidence.needs_user_clarification)
        self.assertEqual(
            data.confidence.clarification_reason,
            "Multiple locations detected with no clear primary destination",
        )

    def test_get_source(self):
        self.assertEqual(self.data_with_values.get_source().title, "Test source")
        self.assertIsNone(self.data.get_source())

    def test_get_locations(self):
        self.assertEqual([loc.name for loc in self.data_with_values.get_locations()], ["New York", "London"])
        self.assertEqual(self.data.get_locations(), [])

    def test_get_activities(self):
        self.assertEqual(self.data_with_values.get_activities(), ["Activity 1"])
        self.assertEqual(self.data.get_activities(), [])

    def test_get_signals(self):
        self.assertEqual(self.data_with_values.get_signals().price, ["Signal 1"])
        self.assertEqual(self.data.get_signals(), TravelSignals())


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