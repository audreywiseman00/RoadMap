import pytest

from parser.models import ContentType

def test_pipeline_returns_extracted_content(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        assert result is not None

def test_primary_destination_detected(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        primary = result.get_locations()[0] if result.get_locations() else None
        assert primary is not None
        assert article["expected_primary_location"] in primary.name

def test_locations_are_populated(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        assert len(result.get_locations()) > 0

def test_activities_are_populated(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        assert len(result.get_activities()) > 0

def test_confidence_flags_set_correctly(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        assert result.confidence.primary_destination_clear is True
        assert result.confidence.needs_user_clarification is False

def test_raw_text_is_not_empty(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"])
        assert len(result.raw_text) > 50  # meaningful content, not a stub

def test_source_metadata_populated(pipeline, known_article_urls):
    for article in known_article_urls:
        result = pipeline.run(article["url"]).get_source()
        assert result.title != ""
        assert result.url == article["url"]
        assert result.content_type == ContentType.ARTICLE