import unittest
from unittest.mock import Mock, patch
import json
from classifier.classifier import TripClassifier
from parser.models import ExtractedData
from classifier.models import ClassifiedTrip, UserPreferences, TripType, BudgetTier

class TestTripClassifier(unittest.TestCase):
    def setUp(self):
        self.llm_client = Mock()
        self.classifier = TripClassifier(self.llm_client)
        self.classifier.MODEL = "test-model"  # Assuming MODEL is set somewhere

    def test_estimate_tokens(self):
        text = "Hello world"
        expected = len(text) // 4
        self.assertEqual(TripClassifier.estimate_tokens(text), expected)

    @patch('classifier.classifier.json.loads')
    def test_classify_normal(self, mock_json_loads):
        content = Mock(spec=ExtractedData)
        content.confidence = Mock()
        content.confidence.needs_user_clarification = False
        preferences = Mock(spec=UserPreferences)

        prompt = "test prompt"
        self.classifier.prompt_builder = Mock()
        self.classifier.prompt_builder.build.return_value = prompt

        self.llm_client.messages.count_tokens.return_value.input_tokens = 100
        response = '{"primary_destination": "Paris", "secondary_destinations": [], "trip_type": "leisure", "budget_tier": "mid_range", "recommended_days": 5, "top_activities": ["Sightseeing"], "classification_confidence": 0.9, "needs_clarification": false}'
        self.llm_client.complete.return_value = response
        # Return a real dict, not a MagicMock, and use lowercase values for enums
        mock_json_loads.return_value = {
            "primary_destination": "Paris",
            "secondary_destinations": [],
            "trip_type": "leisure",
            "budget_tier": "mid_range",
            "recommended_days": 5,
            "top_activities": ["Sightseeing"],
            "classification_confidence": 0.9,
            "needs_clarification": False
        }

        result = self.classifier.classify(content, preferences)

        self.assertIsInstance(result, ClassifiedTrip)
        self.assertEqual(result.primary_destination, "Paris")
        self.assertEqual(result.trip_type, TripType.LEISURE)
        self.assertEqual(result.budget_tier, BudgetTier.MID_RANGE)
        self.assertEqual(result.recommended_days, 5)
        self.assertEqual(result.classification_confidence, 0.9)
        self.assertFalse(result.needs_clarification)

    def test_classify_clarification_needed(self):
        content = Mock(spec=ExtractedData)
        content.confidence = Mock()
        content.confidence.needs_user_clarification = True
        content.confidence.clarification_reason = "Ambiguous destination"
        preferences = Mock(spec=UserPreferences)

        result = self.classifier.classify(content, preferences)

        self.assertIsInstance(result, ClassifiedTrip)
        self.assertEqual(result.primary_destination, "")
        self.assertEqual(result.trip_type, TripType.MIXED)
        self.assertEqual(result.budget_tier, BudgetTier.MID_RANGE)
        self.assertEqual(result.recommended_days, 0)
        self.assertTrue(result.needs_clarification)
        self.assertEqual(result.clarification_questions, ["Ambiguous destination"])

    def test_clarification_needed(self):
        content = Mock(spec=ExtractedData)
        content.confidence = Mock()
        content.confidence.clarification_reason = "Test reason"
        preferences = Mock(spec=UserPreferences)

        result = self.classifier._clarification_needed(content, preferences)

        self.assertIsInstance(result, ClassifiedTrip)
        self.assertEqual(result.primary_destination, "")
        self.assertEqual(result.trip_type, TripType.MIXED)
        self.assertEqual(result.budget_tier, BudgetTier.MID_RANGE)
        self.assertEqual(result.recommended_days, 0)
        self.assertTrue(result.needs_clarification)
        self.assertEqual(result.clarification_questions, ["Test reason"])

if __name__ == '__main__':
    unittest.main()