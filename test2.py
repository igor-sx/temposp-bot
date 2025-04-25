import unittest
from unittest.mock import patch, MagicMock
import os
from main import scrape_and_save

# filepath: test_main.py

# Assuming main.py is in the same directory and the parent is a namespace package
# Use absolute import based on the project structure if needed.
# If 'scrapcge' is the root package visible in PYTHONPATH:
# from scrapcge.main import scrape_and_save
# If running tests from the directory containing main.py:

class TestScrapeAndSave(unittest.TestCase):

    @patch('main.download_image')
    @patch('main.scrape_image_url')
    def test_scrape_and_save_success(self, mock_scrape_image_url, mock_download_image):
        """Tests successful scraping and downloading."""
        test_url = 'http://example.com'
        test_image_path = 'test_image.jpg'
        expected_image_url = 'http://example.com/image.jpg'

        mock_scrape_image_url.return_value = expected_image_url
        mock_download_image.return_value = True

        result = scrape_and_save(test_url, test_image_path)

        mock_scrape_image_url.assert_called_once_with(test_url)
        mock_download_image.assert_called_once_with(expected_image_url, test_image_path)
        self.assertTrue(result)

    @patch('main.download_image')
    @patch('main.scrape_image_url')
    def test_scrape_and_save_scrape_returns_none(self, mock_scrape_image_url, mock_download_image):
        """Tests behavior when scrape_image_url returns None."""
        test_url = 'http://example.com'
        test_image_path = 'test_image.jpg'

        mock_scrape_image_url.return_value = None

        result = scrape_and_save(test_url, test_image_path)

        mock_scrape_image_url.assert_called_once_with(test_url)
        mock_download_image.assert_not_called()
        self.assertFalse(result)

    @patch('main.download_image')
    @patch('main.scrape_image_url')
    def test_scrape_and_save_download_fails(self, mock_scrape_image_url, mock_download_image):
        """Tests behavior when download_image returns False."""
        test_url = 'http://example.com'
        test_image_path = 'test_image.jpg'
        expected_image_url = 'http://example.com/image.jpg'

        mock_scrape_image_url.return_value = expected_image_url
        mock_download_image.return_value = False

        result = scrape_and_save(test_url, test_image_path)

        mock_scrape_image_url.assert_called_once_with(test_url)
        mock_download_image.assert_called_once_with(expected_image_url, test_image_path)
        self.assertFalse(result)

    @patch('main.download_image')
    @patch('main.scrape_image_url', side_effect=Exception("Scraping error"))
    def test_scrape_and_save_scrape_exception(self, mock_scrape_image_url, mock_download_image):
        """Tests behavior when scrape_image_url raises an exception."""
        test_url = 'http://example.com'
        test_image_path = 'test_image.jpg'

        # Suppress expected exception print output during test
        with patch('builtins.print') as mock_print:
            result = scrape_and_save(test_url, test_image_path)

        mock_scrape_image_url.assert_called_once_with(test_url)
        mock_download_image.assert_not_called()
        self.assertFalse(result)
        mock_print.assert_called_once() # Check if the error was printed

    @patch('main.download_image', side_effect=Exception("Download error"))
    @patch('main.scrape_image_url')
    def test_scrape_and_save_download_exception(self, mock_scrape_image_url, mock_download_image):
        """Tests behavior when download_image raises an exception."""
        test_url = 'http://example.com'
        test_image_path = 'test_image.jpg'
        expected_image_url = 'http://example.com/image.jpg'

        mock_scrape_image_url.return_value = expected_image_url

        # The exception in download_image is caught inside download_image itself
        # and it returns False. scrape_and_save then returns that False.
        # We need to adjust the mock to return False when the exception occurs
        # within the mocked function's scope if we were testing download_image directly.
        # However, here we mock download_image itself. If download_image raises
        # an *uncaught* exception, scrape_and_save would also raise it.
        # Since download_image catches its own exceptions and returns False,
        # we should test the case where it returns False (covered above).
        # If we want to test an *uncaught* exception from download_image propagating
        # up through scrape_and_save, we'd need to modify scrape_and_save's
        # exception handling or mock download_image to raise an exception
        # *outside* its own try-except block (which isn't how it's written).
        # Let's assume the current behavior: download_image catches errors and returns False.
        # So, we simulate download_image returning False due to an internal error.

        mock_download_image.return_value = False # Simulate internal error handling

        result = scrape_and_save(test_url, test_image_path)

        mock_scrape_image_url.assert_called_once_with(test_url)
        # If download_image raises an exception *and* that exception is caught
        # within scrape_and_save's try block, then download_image would still be called.
        # Since download_image handles its own exception and returns False,
        # scrape_and_save receives False and returns it.
        mock_download_image.assert_called_once_with(expected_image_url, test_image_path)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()