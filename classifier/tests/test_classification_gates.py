import json
import unittest
from unittest.mock import Mock, patch

from classifier.models import UserPreferences
from classifier.pipeline import ClassificationPipeline
from parser.models import ExtractedData, LocationMention


class TestClassificationPipeline(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        with patch("classifier.pipeline.anthropic.Anthropic", return_value=self.client):
            self.pipeline = ClassificationPipeline(api_key="test-key")
        self.pipeline.prompt_builder = Mock()

    def test_parser_clarification_skips_prompt_construction(self):
        content = ExtractedData()

        result = self.pipeline.run(content, UserPreferences())

        self.assertTrue(result.needs_clarification)
        self.pipeline.prompt_builder.build.assert_not_called()
        self.client.messages.create.assert_not_called()

    def test_validation_issues_skip_prompt_construction(self):
        content = ExtractedData(
            locations=[LocationMention(name="Paris", label="GPE")]
        )

        result = self.pipeline.run(content, UserPreferences())

        self.assertTrue(result.needs_clarification)
        self.assertEqual(
            result.clarification_questions,
            ["No activities were detected in the content."],
        )
        self.pipeline.prompt_builder.build.assert_not_called()
        self.client.messages.create.assert_not_called()

    def test_valid_input_builds_prompt_once_with_context_cap(self):
        content = ExtractedData(
            locations=[LocationMention(name="Paris", label="GPE")],
            activities=["museum visit"],
        )
        preferences = UserPreferences()
        self.pipeline.prompt_builder.build.return_value = "classification prompt"
        self.client.messages.create.return_value.content = [
            Mock(text=json.dumps({
                "primary_destination": "Paris",
                "secondary_destinations": [],
                "trip_type": "cultural",
                "budget_tier": "budget",
                "recommended_days": 4,
                "top_activities": ["museum visit"],
                "confidence": 0.9,
                "needs_clarification": False,
            }))
        ]

        result = self.pipeline.run(content, preferences)

        self.assertEqual(result.primary_destination, "Paris")
        self.pipeline.prompt_builder.build.assert_called_once_with(
            content,
            preferences,
            context_cap=self.pipeline.CONTEXT_SENTENCES_PER_LOCATION,
        )


if __name__ == "__main__":
    unittest.main()
