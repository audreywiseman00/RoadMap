import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import newspaper
import spacy

from parser.models import SourceObject, ExtractedData

nlp = spacy.load("en_core_web_sm")


class ArticleParser:

    def __init__(self, url):
        self.url = url
        self.article = newspaper.Article(url)

    def parse(self):
        self.article.download()
        self.article.parse()

    def get_title(self):
        return self.article.title

    def get_text(self):
        return self.article.text
    
    def get_source_object(self):
        return SourceObject(url=self.url, title=self.get_title(), type="article")
    
    
    def extract_travel_data(self):
        doc = nlp(self.get_text())

        locations = list({ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")})
        orgs = list({ent.text for ent in doc.ents if ent.label_ == "ORG"})
        price_signals = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
        activities = list({chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1})
        location_sentences = [sent.text.strip() for sent in doc.sents
                            if any(e.label_ in ("GPE", "LOC") for e in sent.ents)]

        return ExtractedData(
            source=self.get_source_object(),
            locations=locations,
            orgs=orgs,
            activities=activities,
            signals=price_signals,
            context=location_sentences
        )
    
def main():
    url = "https://www.bbc.com/travel/article/20260312-10-things-all-visitors-to-japan-should-know"
    parser = ArticleParser(url)
    parser.parse()
    print("Title:", parser.get_title())
    print("Text:", parser.get_text())

    print(parser.extract_travel_data())

if __name__ == "__main__":
    main()