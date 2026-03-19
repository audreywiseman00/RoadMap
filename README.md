# ✈️ Vacation Planner App

> Transform social content into personalized travel itineraries — paste an Instagram post, TikTok, or article URL and get a day-by-day vacation plan with a to-do list.

---

## What It Does

Users upload travel content from across the web — Instagram posts, TikTok videos, or travel articles — and the app uses AI to extract destinations, activities, and vibes, then generates a structured itinerary and pre-trip to-do list tailored to their dates, budget, and group size.

---

## Project Roadmap

The app is built across five sequential phases:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Content ingestion | 🔨 In progress |
| 2 | AI understanding | 📋 Planned |
| 3 | Itinerary generation | 📋 Planned |
| 4 | User interaction | 📋 Planned |
| 5 | Enrichment & intelligence | 📋 Planned |

**Phases 1–3 form the MVP** — a user can upload content and receive a useful, personalized itinerary on the other side.

---

## Phase 1: Content Ingestion

The current focus. The app accepts article URLs, parses the body text, and extracts structured travel data.

**Build order:**
1. Article URL parsing ← *current*
2. Plain text paste
3. Instagram (via official API)
4. TikTok (via audio transcription)

### Tech Stack

| Tool | Purpose |
|------|---------|
| `newspaper4k` | Fetch and clean article body text from URLs |
| `spaCy` (`en_core_web_sm`) | Named entity recognition and NLP |
| `BeautifulSoup4` + `requests` | Fallback HTML parsing for tricky sites |
| `playwright` | Headless rendering for JavaScript-heavy pages (optional) |

### Installation

```bash
pip install newspaper4k spacy requests beautifulsoup4
python -m spacy download en_core_web_sm
```

> **Note:** `newspaper4k` depends on `lxml`. If you hit install errors, run:
> ```bash
> pip install lxml[html_clean]
> ```

---

## Core Parsing Module

### Article parser

Fetches a URL and returns cleaned article text plus metadata:

```python
from newspaper import Article

def parse_article(url):
    article = Article(url)
    article.download()
    article.parse()

    return {
        "title": article.title,
        "text": article.text,
        "keywords": article.keywords,
    }
```

### Travel data extractor

Uses spaCy to extract locations, activities, price signals, and contextual sentences from article text:

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_travel_data(text):
    doc = nlp(text)

    locations = list({ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")})
    orgs = list({ent.text for ent in doc.ents if ent.label_ == "ORG"})
    price_signals = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
    activities = list({chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1})
    location_context = [
        sent.text.strip() for sent in doc.sents
        if any(e.label_ in ("GPE", "LOC") for e in sent.ents)
    ]

    return {
        "locations": locations,
        "orgs": orgs,
        "price_signals": price_signals,
        "activities": activities,
        "location_context": location_context
    }
```

### spaCy entity labels used

| Label | What it captures | Travel use |
|-------|-----------------|------------|
| `GPE` | Countries, cities, states | Primary destination extraction |
| `LOC` | Landmarks, mountains, beaches | Points of interest |
| `ORG` | Restaurants, hotels, airlines | Venue discovery |
| `MONEY` | Price mentions | Budget signals |

Beyond NER, two additional spaCy features are used:

- **Noun chunks** (`doc.noun_chunks`) — extracts activity phrases like "sunset hike" or "street food tour" that NER misses
- **Sentence segmentation** (`doc.sents`) — keeps location mentions in context so the AI layer understands *how* a place is described, not just *that* it was mentioned

---

## Data Output Format

The parser returns a structured object passed downstream to the Phase 2 AI layer:

```json
{
  "title": "10 Days in Japan: The Ultimate Itinerary",
  "locations": ["Tokyo", "Kyoto", "Osaka"],
  "orgs": ["Tsukiji Market", "Fushimi Inari Shrine"],
  "price_signals": ["¥1,200", "under $50"],
  "activities": ["ramen tasting", "bullet train ride", "temple walk"],
  "location_context": [
    "Spend your first three days in Tokyo exploring Shibuya and Shinjuku.",
    "Kyoto is best visited in spring when the cherry blossoms are in bloom."
  ]
}
```

The `location_context` field is the most valuable for the downstream AI step — it gives sentence-level context for how each place is described.

---

## Known Limitations (Phase 1)

- **Paywalled articles** — content behind a login will not parse correctly; a user-paste fallback is planned
- **JavaScript-heavy pages** — some modern travel blogs require `playwright` for full rendering
- **Vague destination references** — phrases like "the most magical place I've ever been" won't resolve to a location; a user-confirmation prompt is planned for low-confidence extractions
- **Multi-language content** — the `en_core_web_sm` model is English only; multi-language support is a Phase 2+ consideration

---

## Project Structure

```
vacation-planner/
├── README.md
├── requirements.txt
├── article_parser/
│   ├── __init__.py
│   ├── article_parser.py        # newspaper4k fetching and cleaning
├── tests/
│   └── test_parser.py
└── main.py
```

---

## Contributing

This project is in early development. Phase 1 (article parsing) is the current focus — see the roadmap above for what's coming next.
