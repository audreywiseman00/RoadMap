from .article import ArticleParser
from .models import ExtractedData

class ParserPipeline:
    def __init__(self):
        pass

    def __parser(self, url) -> ArticleParser:
        return ArticleParser(url)

    def run(self, url) -> ExtractedData:
        extracted = self.__parser(url).extract_travel_data()
        return extracted