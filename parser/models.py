class SourceObject:
    
    def __init__(self, url=None, title=None, type=None):
        self.url = url
        self.title = title
        self.type = type
        self.timestamp = None

class ExtractedData:

    def __init__(self, source=None, locations=[], orgs = [], activities=[], signals=[], context = []):
        self.source = source
        self.locations = locations
        self.orgs = orgs
        self.activities = activities
        self.signals = signals
        self.context = context
        self.confidence = None

    def get_source(self):
        return self.source
    
    def get_locations(self):
        return self.locations
    
    def get_activities(self):
        return self.activities
    
    def get_signals(self):
        return self.signals
