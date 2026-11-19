import unittest

from classifier.models import BudgetTier, TripType, UserPreferences
from classifier.pipeline import ClassificationPipeline
from classifier.prompt_builder import PromptBuilder
from parser.models import ExtractedData, LocationMention


class TestClassificationResponseSchema(unittest.TestCase):
    def setUp(self):
        self.pipeline = ClassificationPipeline.__new__(ClassificationPipeline)
        self.response = {
            "primary_destination": "Paris",
            "secondary_destinations": [],
            "trip_type": "leisure",
            "budget_tier": "mid_range",
            "recommended_days": 5,
            "top_activities": ["Sightseeing"],
            "confidence": 0.9,
            "needs_clarification": False,
            "clarification_questions": [],
        }

    def test_accepts_complete_response_matching_prompt_schema(self):
        self.assertTrue(self.pipeline._validate_response(self.response))

    def test_rejects_legacy_confidence_key(self):
        response = self.response.copy()
        response["classification_confidence"] = response.pop("confidence")

        self.assertFalse(self.pipeline._validate_response(response))

    def test_rejects_invalid_confidence_and_days(self):
        for field, value in (("confidence", 1.1), ("recommended_days", True)):
            with self.subTest(field=field):
                response = self.response.copy()
                response[field] = value
                self.assertFalse(self.pipeline._validate_response(response))

    def test_rejects_missing_schema_fields_and_wrong_types(self):
        missing_field = self.response.copy()
        del missing_field["clarification_questions"]
        wrong_type = self.response.copy()
        wrong_type["top_activities"] = "Sightseeing"

        self.assertFalse(self.pipeline._validate_response(missing_field))
        self.assertFalse(self.pipeline._validate_response(wrong_type))
        self.assertFalse(self.pipeline._validate_response([]))

    def test_prompt_uses_pipeline_field_names_and_enum_values(self):
        content = ExtractedData(
            locations=[LocationMention(name="Paris", label="GPE")],
            activities=["Sightseeing"],
        )
        prompt = PromptBuilder().build(
            content,
            UserPreferences(
                budget_tier=BudgetTier.MID_RANGE,
                travel_style=TripType.LEISURE,
            ),
        )

        self.assertIn('"confidence": "number between 0 and 1"', prompt)
        self.assertNotIn('"classification_confidence"', prompt)
        self.assertIn("leisure", prompt)
        self.assertIn("Budget: mid_range", prompt)
        self.assertIn("Travel style: leisure", prompt)


if __name__ == "__main__":
    unittest.main()
