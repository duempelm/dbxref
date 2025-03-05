#IMPORT
import json
import re
import unittest
from unittest.mock import patch
from urllib3.response import HTTPResponse
from main import resolve_id, available

#FUNCTIONS
def is_valid_regex(pattern):
    """
    Tests if a given string compiles successful to a regular expression.

    Parameters:
        pattern (string): regular expression string.

    Returns:
        boolean: True if string compiles to regular expression, False if not.
    """

    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


#TESTING CONFIG FORMAT ####################################################################################
class TestConfigFormat(unittest.TestCase):
    def setUp(self):
        """Load the config file before each test."""
        try:
            with open('config.json', 'r') as f:
                self.config_data = json.load(f)
        except FileNotFoundError:
            self.config_data = None  # Handle the case where the file doesn't exist

    def test_config_exists(self):
        """Check if the config file exists and was loaded."""
        self.assertIsNotNone(self.config_data, "config.json file not found or could not be loaded")

    def test_config_is_list(self):
        """Check if the loaded config is a list."""
        self.assertIsInstance(self.config_data, list, "Config data should be a list")

    def test_config_list_not_empty(self):
        """Check if the list is not empty"""
        self.assertTrue(len(self.config_data) > 0, "Config list should not be empty")

    def test_config_elements_are_dictionaries(self):
        """Check if each element in the list is a dictionary."""
        if self.config_data: # Check if config_data is not None and not empty
            for item in self.config_data:
                self.assertIsInstance(item, dict, "Each element in the list should be a dictionary")

    def test_config_dictionaries_have_required_keys(self):
        """Check if each dictionary has the keys 'regexp' and 'html'."""
        if self.config_data: # Check if config_data is not None and not empty
            for item in self.config_data:
                self.assertIn("regexp", item, "Each dictionary should have a 'regexp' key")
                self.assertIn("html", item, "Each dictionary should have an 'html' key")

    def test_config_regexp_is_string(self):
        """Check if the value of 'regexp' is a string."""
        if self.config_data:
            for item in self.config_data:
                if "regexp" in item: #Check if regexp is in item before accessing it.
                    self.assertIsInstance(item["regexp"], str, "The value of 'regexp' should be a string")

    def test_config_regexp_is_valid(self):
        """Check if the value of 'regexp' is a valid regular expression."""
        if self.config_data:
            for item in self.config_data:
                if "regexp" in item:
                    self.assertTrue(is_valid_regex(item['regexp']), "The value of 'regexp' should compile to a valid regular expression")

    def test_config_html_is_string(self):
        """Check if the value of 'html' is a string."""
        if self.config_data:
            for item in self.config_data:
                if "html" in item:  #Check if html is in item before accessing it.
                    self.assertIsInstance(item["html"], str, "The value of 'html' should be a string")

    def test_config_html_has_dollar(self):
        """Check if the value of 'html' contains '$' marking the position where the id string should be inserted."""
        if self.config_data:
            for item in self.config_data:
                if "html" in item:
                    self.assertTrue("$" in item["html"], "The value of 'html' should have a '$' marking the position where the id string should be inserted")

# TESTING RESOLVE_ID ######################################################################################
class TestResolveId(unittest.TestCase):
    @patch('main.load_config')
    def test_matching_id(self, mock_load_config):
        mock_load_config.return_value = [
            {"regexp": "GO:\\d{7}", "html": "https://example.com/$"}
        ]
        result = resolve_id("GO:0003870")
        self.assertEqual(result, "https://example.com/GO:0003870")

    @patch('main.load_config')
    def test_non_matching_id(self, mock_load_config):
        mock_load_config.return_value = [
            {"regexp": "GO:\\d{7}", "html": "https://example.com/$"}
        ]
        result = resolve_id("IPR000001")
        self.assertIsNone(result)

    @patch('main.load_config')
    def test_empty_string_id(self, mock_load_config):
        mock_load_config.return_value = [
            {"regexp": "GO:\\d{7}", "html": "https://example.com/$"}
        ]
        result = resolve_id("")
        self.assertIsNone(result)

    @patch('main.load_config')
    def test_different_regexp_patterns(self, mock_load_config):
        mock_load_config.return_value = [
            {"regexp": "GO:\\d{7}", "html": "https://go.example.com/$"},
            {"regexp": "IPR\\d{6}", "html": "https://ipr.example.com/$"}
        ]
        result1 = resolve_id("GO:0003870")
        result2 = resolve_id("IPR000001")
        self.assertEqual(result1, "https://go.example.com/GO:0003870")
        self.assertEqual(result2, "https://ipr.example.com/IPR000001")

    @patch('main.load_config')
    def test_special_characters(self, mock_load_config):
        mock_load_config.return_value = [
            {"regexp": "SPEC[!@#$%^&*]\\d+", "html": "https://example.com/$"}
        ]
        result = resolve_id("SPEC@123")
        self.assertEqual(result, "https://example.com/SPEC@123")

    @patch('main.load_config')
    def test_empty_config(self, mock_load_config):
        mock_load_config.return_value = []
        result = resolve_id("GO:0003870")
        self.assertIsNone(result)

# TESTING AVAILABLE #######################################################################################
class TestAvailable(unittest.TestCase):
    @patch('main.request')
    def test_successful_request(self, mock_request):
        mock_response = HTTPResponse(status=200)
        mock_request.return_value = mock_response
        self.assertEqual(available("http://example.com"), 200)

    @patch('main.request')
    def test_not_found(self, mock_request):
        mock_response = HTTPResponse(status=404)
        mock_request.return_value = mock_response
        self.assertEqual(available("http://example.com/notfound"), 404)

    @patch('main.request')
    def test_server_error(self, mock_request):
        mock_response = HTTPResponse(status=500)
        mock_request.return_value = mock_response
        self.assertEqual(available("http://example.com/error"), 500)

    @patch('main.request')
    def test_redirect(self, mock_request):
        mock_response = HTTPResponse(status=301)
        mock_request.return_value = mock_response
        self.assertEqual(available("http://example.com/old"), 301)

    @patch('main.request')
    def test_invalid_url(self, mock_request):
        mock_request.side_effect = ValueError("Invalid URL")
        with self.assertRaises(ValueError):
            available("not_a_valid_url")

    @patch('main.request')
    def test_non_existent_domain(self, mock_request):
        mock_request.side_effect = Exception("Name or service not known")
        with self.assertRaises(Exception):
            available("http://thisdoesnotexist.example")

    @patch('main.request')
    def test_timeout(self, mock_request):
        mock_request.side_effect = Exception("Request timed out")
        with self.assertRaises(Exception):
            available("http://veryslow.example")

    @patch('main.request')
    def test_https_protocol(self, mock_request):
        mock_response = HTTPResponse(status=200)
        mock_request.return_value = mock_response
        self.assertEqual(available("https://example.com"), 200)

if __name__ == '__main__':
    unittest.main()
