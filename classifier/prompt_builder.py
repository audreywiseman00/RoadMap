from classifier.models import UserPreferences
from parser.models import ExtractedData

class PromptBuilder:
    def build(self, content: ExtractedContent, preferences: UserPreferences, context_cap: int = 2) -> str:
        context_sentences = [
            sentence
            for location in content.locations
            for sentence in location.capped_context(max_sentences=context_cap)
        ]

        # deduplicate in case the same sentence appears under multiple locations
        seen = set()
        unique_context = []
        for s in context_sentences:
            if s not in seen:
                seen.add(s)
                unique_context.append(s)

        return f"""
You are classifying travel content to generate a vacation itinerary.

DETECTED CONTENT:
Locations: {content.locations}
Activities: {content.activities}
Price signals: {content.signals.price}
Vibe signals: {content.signals.vibe}
Season signals: {content.signals.season}

KEY CONTEXT SENTENCES:
{chr(10).join(unique_context)}

USER PREFERENCES:
Group size: {preferences.group_size}
Budget: {preferences.budget_tier or "not specified"}
Travel style: {preferences.travel_style or "not specified"}
Trip length: {preferences.start_date} to {preferences.end_date or "not specified"}

Respond in JSON only. No preamble. Schema:
{{
    "primary_destination": "string",
    "secondary_destinations": ["string"],
    "trip_type": "adventure|cultural|food|relaxation|mixed",
    "budget_tier": "budget|mid_range|luxury",
    "recommended_days": number,
    "top_activities": ["string"],
    "classification_confidence": number between 0 and 1,
    "needs_clarification": boolean,
    "clarification_questions": ["string"]
}}
"""