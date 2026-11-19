import unittest
from unittest.mock import Mock, patch, MagicMock

from parser.article import ArticleParser
from parser.models import SourceObject, ExtractedData



class TestArticleParser(unittest.TestCase):

    def setUp(self):
        self.url = "https://example.com/article"
        self.parser = ArticleParser(self.url)

    def test_init(self):
        self.assertEqual(self.parser.url, self.url)
        self.assertIsNotNone(self.parser.article)

    @patch('newspaper.Article')
    def test_parse(self, mock_article):
        mock_instance = MagicMock()
        mock_article.return_value = mock_instance
        
        parser = ArticleParser(self.url)
        parser.parse()
        
        mock_instance.download.assert_called_once()
        mock_instance.parse.assert_called_once()

    @patch('newspaper.Article')
    def test_get_title(self, mock_article):
        mock_instance = MagicMock()
        mock_instance.title = "Test Article Title"
        mock_article.return_value = mock_instance
        
        parser = ArticleParser(self.url)
        self.assertEqual(parser.get_title(), "Test Article Title")

    @patch('newspaper.Article')
    def test_get_text(self, mock_article):
        mock_instance = MagicMock()
        mock_instance.text = "Test article body text"
        mock_article.return_value = mock_instance
        
        parser = ArticleParser(self.url)
        self.assertEqual(parser.get_text(), "Test article body text")

    @patch('newspaper.Article')
    def test_get_source_object(self, mock_article):
        mock_instance = MagicMock()
        mock_instance.title = "Test Title"
        mock_article.return_value = mock_instance
        
        parser = ArticleParser(self.url)
        source = parser.get_source_object()
        
        self.assertIsInstance(source, SourceObject)
        self.assertEqual(source.url, self.url)
        self.assertEqual(source.title, "Test Title")
        self.assertEqual(source.type, "article")

    @patch('parser.article.nlp')
    @patch('newspaper.Article')
    def test_extract_travel_data(self, mock_article, mock_nlp):
        mock_instance = MagicMock()
        mock_instance.text = "Paris and London are cities. Hotel costs $200."
        mock_article.return_value = mock_instance
        
        mock_ent1 = Mock(text="Paris", label_="GPE")
        repeated_paris = Mock(text="Paris", label_="GPE")
        london = Mock(text="London", label_="GPE")
        money = Mock(text="$200", label_="MONEY")
        
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, repeated_paris, london, money]
        paris_sentence = Mock(
            text="Paris and London are cities.",
            ents=[mock_ent1, london],
        )
        repeated_sentence = Mock(
            text="Paris is known for its cafes.",
            ents=[repeated_paris],
        )
        mock_doc.sents = [paris_sentence, repeated_sentence]
        mock_doc.noun_chunks = []
        mock_nlp.return_value = mock_doc
        
        parser = ArticleParser(self.url)
        result = parser.extract_travel_data()
        
        self.assertIsInstance(result, ExtractedData)
        locations = {location.name: location for location in result.locations}
        self.assertEqual(list(locations), ["Paris", "London"])
        self.assertEqual(locations["Paris"].frequency, 2)
        self.assertTrue(result.confidence.primary_destination_clear)
        self.assertFalse(result.confidence.needs_user_clarification)
        self.assertEqual(
            locations["Paris"].context,
            ["Paris and London are cities.", "Paris is known for its cafes."],
        )
        self.assertEqual(locations["London"].context, ["Paris and London are cities."])
        self.assertEqual(result.signals.price, ["$200"])
        self.assertEqual(result.signals.vibe, [])
        self.assertEqual(result.signals.season, [])


if __name__ == '__main__':
    unittest.main()