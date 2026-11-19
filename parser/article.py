import newspaper
import spacy

from .models import ExtractedData, LocationMention, SourceObject, TravelSignals

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
        self.parse()  # Ensure article is parsed before extracting
        doc = nlp(self.get_text())

        locations_by_name = {}
        for ent in doc.ents:
            if ent.label_ not in ("GPE", "LOC"):
                continue
            key = ent.text.strip().casefold()
            mention = locations_by_name.get(key)
            if mention is None:
                mention = LocationMention(name=ent.text, label=ent.label_)
                locations_by_name[key] = mention
            else:
                mention.frequency += 1

        for sent in doc.sents:
            sentence = sent.text.strip()
            if not sentence:
                continue
            for ent in sent.ents:
                if ent.label_ not in ("GPE", "LOC"):
                    continue
                mention = locations_by_name.get(ent.text.strip().casefold())
                if mention is not None and sentence not in mention.context:
                    mention.context.append(sentence)

        orgs = list(dict.fromkeys(
            ent.text for ent in doc.ents if ent.label_ == "ORG"
        ))
        price_signals = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
        activities = list(dict.fromkeys(
            chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1
        ))

        return ExtractedData(
            source=self.get_source_object(),
            locations=list(locations_by_name.values()),
            orgs=orgs,
            activities=activities,
            signals=TravelSignals(price=price_signals),
            raw_text=self.get_text()
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