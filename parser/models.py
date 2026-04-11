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

class Location:
    def __init__(self, name):
        self.name = name

class SourceObject:
    
    def __init__(self, url=None, title=None, type=None):
        self.url = url
        self.title = title
        self.type = type
        self.timestamp = None
        self.content_type = ContentType.ARTICLE if type == "article" else None

class ExtractedData:

    def __init__(self, source=None, locations=[], orgs = [], activities=[], signals=[], context = [], raw_text=""):
        self.source = source
        self.locations = [Location(loc) for loc in locations]  # Convert strings to Location objects
        self.orgs = orgs
        self.activities = activities
        self.signals = signals
        self.context = context
        self.raw_text = raw_text
        self.confidence = Confidence()
        
        # Set confidence flags
        if not self.locations:
            self.confidence.needs_user_clarification = True
            self.confidence.clarification_reason = "No locations detected"
        elif len(self.locations) == 1:
            self.confidence.primary_destination_clear = True

    def get_source(self):
        return self.source
    
    def get_locations(self):
        return self.locations
    
    def get_activities(self):
        return self.activities
    
    def get_signals(self):
        return self.signals
