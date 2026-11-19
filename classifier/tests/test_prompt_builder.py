import unittest

from classifier.models import UserPreferences
from classifier.prompt_builder import PromptBuilder
from parser.models import ExtractedData, LocationMention, TravelSignals


class TestPromptBuilder(unittest.TestCase):
    def test_build_uses_structured_locations_and_signals(self):
        content = ExtractedData(
            locations=[
                LocationMention(
                    name="Tokyo",
                    label="GPE",
                    frequency=2,
                    context=["Tokyo is lively.", "Try the local markets."],
                ),
                LocationMention(
                    name="Kyoto",
                    label="GPE",
                    context=["Kyoto is known for temples.", "Tokyo is lively."],
                ),
            ],
            activities=["market visit"],
            signals=TravelSignals(
                price=["under $50"],
                vibe=["relaxed"],
                season=["spring"],
            ),
        )

        prompt = PromptBuilder().build(
            content,
            UserPreferences(),
            context_cap=2,
        )

        self.assertIn("Locations: ['Tokyo', 'Kyoto']", prompt)
        self.assertIn("Price signals: ['under $50']", prompt)
        self.assertIn("Vibe signals: ['relaxed']", prompt)
        self.assertIn("Season signals: ['spring']", prompt)
        self.assertEqual(prompt.count("Tokyo is lively."), 1)
        self.assertIn("Try the local markets.", prompt)
        self.assertIn("Kyoto is known for temples.", prompt)

    def test_context_cap_applies_per_location(self):
        content = ExtractedData(
            locations=[
                LocationMention(
                    name="Paris",
                    label="GPE",
                    context=["First Paris sentence.", "Second Paris sentence."],
                )
            ]
        )

        prompt = PromptBuilder().build(
            content,
            UserPreferences(),
            context_cap=1,
        )

        self.assertIn("First Paris sentence.", prompt)
        self.assertNotIn("Second Paris sentence.", prompt)


if __name__ == "__main__":
    unittest.main()
