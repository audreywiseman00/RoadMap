from dataclasses import dataclass, field
from enum import Enum

class ContentType(Enum):
    ARTICLE = "article"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    PASTE = "paste"

class Confidence:
    def __init__(self):
        self.primary_destination_clear = False
        self.needs_user_clarification = False
        self.clarification_reason = None

class SourceObject:
    
    def __init__(self, url=None, title=None, type=None):
        self.url = url
        self.title = title
        self.type = type
        self.timestamp = None
        self.content_type = ContentType.ARTICLE if type == "article" else None

@dataclass
class LocationMention:
    name: str
    label: str
    frequency: int = 1
    context: list[str] = field(default_factory=list)

@dataclass
class TravelSignals:
    price: list[str] = field(default_factory=list)
    vibe: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)

@dataclass
class ExtractedData:
    source: SourceObject | None = None
    locations: list[LocationMention] = field(default_factory=list)
    orgs: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    signals: TravelSignals = field(default_factory=TravelSignals)
    raw_text: str = ""
    confidence: Confidence = field(init=False, default_factory=Confidence)

    def __post_init__(self):
        if not self.locations:
            self.confidence.clarification_reason = "No locations detected"
            self.confidence.needs_user_clarification = True
            return

        frequencies = [location.frequency for location in self.locations]
        highest_frequency = max(frequencies)
        has_unique_leader = frequencies.count(highest_frequency) == 1
        self.confidence.primary_destination_clear = has_unique_leader
        self.confidence.needs_user_clarification = not has_unique_leader
        self.confidence.clarification_reason = (
            None
            if has_unique_leader
            else "Multiple locations detected with no clear primary destination"
        )

    def get_source(self):
        return self.source
    
    def get_locations(self):
        return self.locations
    
    def get_activities(self):
        return self.activities
    
    def get_signals(self):
        return self.signals
