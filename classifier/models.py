from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from parser.models import ExtractedData

class TripType(Enum):
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    FOOD = "food"
    RELAXATION = "relaxation"
    LEISURE = "leisure"
    MIXED = "mixed"

class BudgetTier(Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"

@dataclass
class LocationMention:
    name: str
    label: str
    frequency: int
    sentiment_context: list[str] = field(default_factory=list)

    def capped_context(self, max_sentences: int = 2) -> list[str]:
        return self.sentiment_context[:max_sentences]

@dataclass
class UserPreferences:
    group_size: int = 1
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_tier: Optional[BudgetTier] = None
    travel_style: Optional[TripType] = None

    def trip_length_days(self) -> Optional[int]:
        if self.start_date and self.end_date:
            from datetime import date
            start = date.fromisoformat(self.start_date)
            end = date.fromisoformat(self.end_date)
            return (end - start).days
        return None


@dataclass
class ClassificationResult:
    primary_destination: str
    secondary_destinations: list[str]
    trip_type: TripType
    budget_tier: BudgetTier
    recommended_days: int
    top_activities: list[str]
    confidence: float           # 0.0 – 1.0
    needs_clarification: bool
    clarification_questions: list[str] = field(default_factory=list)

@dataclass
class ClassifiedTrip:
    source: ExtractedData            # full parser output carried forward
    preferences: UserPreferences
    result: ClassificationResult
    model_used: str                     # e.g. "claude-sonnet-4-6"
    classified_at: str                  # ISO timestamp

    @property
    def primary_destination(self) -> str:
        return self.result.primary_destination

    def is_ready_for_itinerary(self) -> bool:
        return (
            not self.result.needs_clarification
            and self.result.confidence >= 0.7
            and bool(self.result.primary_destination)
        )

    @property
    def clarification_questions(self) -> list[str]:
        return self.result.clarification_questions if self.result.needs_clarification else []

    @property
    def trip_type(self):
        return self.result.trip_type

    @property
    def budget_tier(self):
        return self.result.budget_tier

    @property
    def recommended_days(self):
        return self.result.recommended_days

    @property
    def needs_clarification(self):
        return self.result.needs_clarification

    @property
    def classification_confidence(self):
        return self.result.confidence