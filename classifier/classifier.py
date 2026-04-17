from email.mime import text
import json
from urllib import response

from typer import prompt
from parser.models import ExtractedData
from .models import ClassifiedTrip, UserPreferences
from .prompt_builder import PromptBuilder

class TripClassifier:
    def __init__(self, llm_client):
        self.client = llm_client       # your OpenAI/Anthropic client
        self.prompt_builder = PromptBuilder()

    # rough estimate — Anthropic tokenizes at ~4 chars per token
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
    
    def classify(self, content: ExtractedData, preferences: UserPreferences) -> ClassifiedTrip:
        if content.confidence.needs_user_clarification:
            return self._clarification_needed(content, preferences)

        prompt = self.prompt_builder.build(content, preferences)
        print(f"Estimated prompt tokens: {self.estimate_tokens(prompt)}")
        
        
        input_tokens = self.client.messages.count_tokens(
                                    model=self.MODEL,
                                    messages=[{"role": "user", "content": prompt}]).input_tokens

        print(f"Exact token count: {input_tokens}")
        response = self.client.complete(prompt)
        data = json.loads(response)

        return ClassifiedTrip(
            source=content,
            primary_destination=data["primary_destination"],
            secondary_destinations=data["secondary_destinations"],
            trip_type=TripType(data["trip_type"]),
            budget_tier=BudgetTier(data["budget_tier"]),
            recommended_days=data["recommended_days"],
            top_activities=data["top_activities"],
            preferences=preferences,
            classification_confidence=data["classification_confidence"],
            needs_clarification=data["needs_clarification"],
            clarification_questions=data.get("clarification_questions", [])
        )

    def _clarification_needed(self, content, preferences) -> ClassifiedTrip:
        # Returns a minimal ClassifiedTrip flagged for user input
        # before any AI call is made — saves tokens on bad input
        return ClassifiedTrip(
            source=content,
            primary_destination="",
            secondary_destinations=[],
            trip_type=TripType.MIXED,
            budget_tier=BudgetTier.MID_RANGE,
            recommended_days=0,
            top_activities=[],
            preferences=preferences,
            classification_confidence=0.0,
            needs_clarification=True,
            clarification_questions=[content.confidence.clarification_reason]
        )