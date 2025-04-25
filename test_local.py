import unittest
from unittest.mock import patch, MagicMock
from main import scrape_image_url

# test_main.py
import requests # Import requests for exception testing

# Assuming main.py is in the same directory
# Use absolute import as the parent is a namespace package

class TestScrapeImageUrl(unittest.TestCase):

    @patch('main.requests.get')
    def test_scrape_image_url_success(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate the relevant part of the HTML structure
        mock_response.text = """
        <html>
            <head>
                <style>
                    .someOtherClass { background: blue; }
                    .condTempo {
                        background: transparent url(../img/condTempo/ceu_claro_dia.png) no-repeat center center;
                        width: 100%;
                        height: 100%;
                    }
                </style>
            </head>
            <body></body>
        </html>
        """
        mock_get.return_value = mock_response

        test_url = 'https://www.example.com/page.jsp'
        expected_url = 'https://www.example.com/img/condTempo/ceu_claro_dia.png'
        actual_url = scrape_image_url(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(actual_url, expected_url)

    @patch('main.requests.get')
    def test_scrape_image_url_not_found(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate HTML without the target style or URL
        mock_response.text = """
        <html>
            <head>
                <style>
                    .someOtherClass { background: blue; }
                </style>
            </head>
            <body></body>
        </html>
        """
        mock_get.return_value = mock_response

        test_url = 'https://www.example.com/page.jsp'
        actual_url = scrape_image_url(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertIsNone(actual_url)

    @patch('main.requests.get')
    def test_scrape_image_url_no_style_tag(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate HTML without any style tag
        mock_response.text = """
        <html>
            <head></head>
            <body><p>No style here</p></body>
        </html>
        """
        mock_get.return_value = mock_response

        test_url = 'https://www.example.com/page.jsp'
        # Expecting AttributeError because bs.find('style') will be None
        with self.assertRaises(AttributeError):
            scrape_image_url(test_url)
        mock_get.assert_called_once_with(test_url)


    @patch('main.requests.get')
    def test_scrape_image_url_request_error(self, mock_get):
        # Configure the mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Test connection error")

        test_url = 'https://www.example.com/page.jsp'
        # Expecting the function to propagate the requests exception
        with self.assertRaises(requests.exceptions.RequestException):
            scrape_image_url(test_url)
        mock_get.assert_called_once_with(test_url)

if __name__ == '__main__':
    unittest.main()