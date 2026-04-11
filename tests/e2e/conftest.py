import pytest
from unittest.mock import MagicMock, Mock, patch
from parser.pipeline import ParserPipeline

@pytest.fixture(scope="session")
def pipeline():
    return ParserPipeline()

@pytest.fixture
def known_article_urls():
    return [
        {
            "url": "https://www.nytimes.com/2025/04/30/t-magazine/japan-travel-guide.html",
            "expected_primary_location": "Paris",  # Mock returns Paris and London
            "expected_content_type": "article"
        },
        {
            "url": "https://www.ricksteves.com/europe/italy/rome",
            "expected_primary_location": "Paris",  # Mock returns Paris and London
            "expected_content_type": "article"
        }
    ]

@pytest.fixture(autouse=True)
def mock_newspaper_article():
    """Mock newspaper.Article to avoid hitting the network in e2e tests."""
    with patch('newspaper.Article') as mock_article_class:
        mock_instance = MagicMock()
        mock_instance.title = "Test Article Title"
        mock_instance.text = "Paris is a great city to visit. The hotel costs $200 per night."
        
        # Mock the download and parse methods
        mock_instance.download.return_value = None
        mock_instance.parse.return_value = None
        
        mock_article_class.return_value = mock_instance
        yield mock_article_class

@pytest.fixture(autouse=True)
def mock_spacy_load():
    """Mock spacy.load to avoid loading the model in e2e tests."""
    with patch('parser.article.nlp') as mock_nlp:
        
        # Create mock entities - only one location for primary_destination_clear
        mock_ent1 = Mock()
        mock_ent1.text = "Paris"
        mock_ent1.label_ = "GPE"
        
        mock_ent2 = Mock()
        mock_ent2.text = "$200"
        mock_ent2.label_ = "MONEY"
        
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2]  # Only Paris as location
        mock_doc.noun_chunks = [Mock(text="great cities"), Mock(text="luxury hotel")]
        
        # Mock sentences
        mock_sent = Mock()
        mock_sent.text = "Paris is a great city to visit."
        mock_sent.ents = [mock_ent1]  # Sentence contains Paris
        mock_doc.sents = [mock_sent]
        
        mock_nlp.return_value = mock_doc
        yield mock_nlp