import unittest
from unittest.mock import patch
from io import StringIO

from main import scrape_image_url

class TestScrapeImage(unittest.TestCase):
    @patch('requests.get')  # mock requests
    def test_scrape_image_url(self, mock_get):
        # mock HTML response with fake CSS style
        mock_html = """
        <html>
            <style>
                .condTempo { background: url('test.png') }
            </style>
        </html>
        """
        mock_get.return_value.text = mock_html

        result = scrape_image_url("http://fakeurl.com")
        
        self.assertIn("test.png", result)  # check if 'test.png' is in the result

if __name__ == '__main__':
    unittest.main()