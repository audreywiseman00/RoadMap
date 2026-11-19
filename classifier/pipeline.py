import json
import anthropic
from datetime import datetime, timezone
from .models import (
    ClassifiedTrip, ClassificationResult,
    UserPreferences, TripType, BudgetTier
)
from .prompt_builder import PromptBuilder
from parser.models import ExtractedData

class ClassificationPipeline:

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 400
    MAX_RETRIES = 2
    MIN_CONFIDENCE = 0.7
    CONTEXT_SENTENCES_PER_LOCATION = 2

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_builder = PromptBuilder()

    def run(self, content: ExtractedData, preferences: UserPreferences) -> ClassifiedTrip:
        # Gate 1: check parser confidence before building a prompt or calling the model.
        if content.confidence.needs_user_clarification:
            return self._needs_clarification(content, preferences, [
                content.confidence.clarification_reason
            ])

        # Gate 2: check we have enough to classify.
        validation_issues = self._validate_inputs(content, preferences)
        if validation_issues:
            return self._needs_clarification(content, preferences, validation_issues)

        prompt = self.prompt_builder.build(
            content,
            preferences,
            context_cap=self.CONTEXT_SENTENCES_PER_LOCATION
        )
        raw_result = self._call_with_retry(prompt)

        if raw_result is None:
            return self._needs_clarification(content, preferences, [
                "Classification failed after retries — please try again."
            ])

        result = self._parse_result(raw_result)
        return ClassifiedTrip(
            source=content,
            preferences=preferences,
            result=result,
            model_used=self.MODEL,
            classified_at=datetime.now(timezone.utc).isoformat()
        )

    def _validate_inputs(self, content: ExtractedData, preferences: UserPreferences) -> list[str]:
        issues = []
        if not content.locations:
            issues.append("No destinations were detected in the content.")
        if not content.activities:
            issues.append("No activities were detected in the content.")
        if preferences.trip_length_days() is not None and preferences.trip_length_days() < 1:
            issues.append("Trip end date must be after start date.")
        return issues

    def _call_with_retry(self, prompt: str) -> dict | None:
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=self.MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text
                data = json.loads(text)
                if self._validate_response(data):
                    return data
            except json.JSONDecodeError:
                if attempt == self.MAX_RETRIES - 1:
                    return None
            except anthropic.APIError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
        return None

    def _validate_response(self, data: dict) -> bool:
        required = [
            "primary_destination", "trip_type", "budget_tier",
            "recommended_days", "top_activities", "confidence",
            "needs_clarification"
        ]
        if not all(k in data for k in required):
            return False
        if data["trip_type"] not in [t.value for t in TripType]:
            return False
        if data["budget_tier"] not in [b.value for b in BudgetTier]:
            return False
        return True

    def _parse_result(self, data: dict) -> ClassificationResult:
        return ClassificationResult(
            primary_destination=data["primary_destination"],
            secondary_destinations=data.get("secondary_destinations", []),
            trip_type=TripType(data["trip_type"]),
            budget_tier=BudgetTier(data["budget_tier"]),
            recommended_days=data["recommended_days"],
            top_activities=data["top_activities"],
            confidence=data["confidence"],
            needs_clarification=data["needs_clarification"],
            clarification_questions=data.get("clarification_questions", [])
        )

    def _needs_clarification(
        self,
        content: ExtractedData,
        preferences: UserPreferences,
        questions: list[str]
    ) -> ClassifiedTrip:
        return ClassifiedTrip(
            source=content,
            preferences=preferences,
            result=ClassificationResult(
                primary_destination="",
                secondary_destinations=[],
                trip_type=TripType.MIXED,
                budget_tier=BudgetTier.MID_RANGE,
                recommended_days=0,
                top_activities=[],
                confidence=0.0,
                needs_clarification=True,
                clarification_questions=questions
            ),
            model_used=self.MODEL,
            classified_at=datetime.now(timezone.utc).isoformat()
        )