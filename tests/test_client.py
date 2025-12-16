import unittest
import json
import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.client import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "dummy_key"
        self.client = LLMClient(self.api_key)
        self.prompt_template = "User: {user_input}, Candidates: {candidates}"

    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_classify_intent_success(self, mock_request, mock_urlopen):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "查询"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test data
        user_input = "我要查余额"
        candidates = ["充值", "查询"]
        
        # Call method
        result = self.client.classify_intent(user_input, candidates, self.prompt_template)
        
        # Verify result
        self.assertEqual(result, "查询")
        
        # Verify request construction
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "https://api.deepseek.com/chat/completions")
        
        # Verify payload
        payload = json.loads(kwargs['data'].decode('utf-8'))
        self.assertEqual(payload['model'], "deepseek-chat")
        self.assertIn("我要查余额", payload['messages'][1]['content'])
        
        # Verify headers
        headers = kwargs['headers']
        self.assertEqual(headers['Authorization'], "Bearer dummy_key")

    @patch("urllib.request.urlopen")
    def test_classify_intent_partial_match(self, mock_urlopen):
        # The LLM might return a sentence like "The user wants to 查询"
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "User intent is 查询"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.classify_intent("test", ["查询"], self.prompt_template)
        self.assertEqual(result, "查询")

    @patch("urllib.request.urlopen")
    def test_classify_intent_no_match(self, mock_urlopen):
        # The LLM returns something completely different
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "Unknown intent"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.classify_intent("test", ["查询"], self.prompt_template)
        self.assertEqual(result, "None")

    @patch("urllib.request.urlopen")
    def test_classify_intent_network_error(self, mock_urlopen):
        # Simulate network error
        mock_urlopen.side_effect = Exception("Network error")

        result = self.client.classify_intent("test", ["查询"], self.prompt_template)
        self.assertEqual(result, "None")

if __name__ == "__main__":
    unittest.main()
