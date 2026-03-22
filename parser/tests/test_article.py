import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from parser.article import ArticleParser
from source import SourceObject
from extracted_data import ExtractedData



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

    @patch('newspaper.Article')
    @patch('spacy.load')
    def test_extract_travel_data(self, mock_spacy, mock_article):
        mock_instance = MagicMock()
        mock_instance.text = "Paris and London are cities. Hotel costs $200."
        mock_article.return_value = mock_instance
        
        mock_nlp = MagicMock()
        mock_spacy.return_value = mock_nlp
        
        mock_ent1 = Mock(text="Paris", label_="GPE")
        mock_ent2 = Mock(text="London", label_="GPE")
        mock_ent3 = Mock(text="$200", label_="MONEY")
        
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2, mock_ent3]
        mock_nlp.return_value = mock_doc
        
        parser = ArticleParser(self.url)
        result = parser.extract_travel_data()
        
        self.assertIsInstance(result, ExtractedData)
        self.assertIn("Paris", result.locations)
        self.assertIn("London", result.locations)
        self.assertIn("200", result.signals)


if __name__ == '__main__':
    unittest.main()