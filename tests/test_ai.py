import os
import unittest
from unittest.mock import patch

from app.ai import AIUnavailable, generate_grounded_draft


class FakeResponse:
    output_text = "Thanks for contacting support. We can help review the duplicate charge."


class FakeResponses:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class AITests(unittest.TestCase):
    def test_missing_api_key_is_safe(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AIUnavailable):
                generate_grounded_draft("duplicate charge", "billing", [])

    def test_generation_uses_configured_model_and_grounding(self):
        fake_client = FakeClient()
        sources = [{
            "id": "billing-duplicate-charge",
            "title": "Duplicate charges",
            "content": "Collect the transaction details for review.",
        }]
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "test-model",
        }, clear=True), patch("app.ai._client", return_value=fake_client):
            result = generate_grounded_draft("I was charged twice", "billing", sources)

        self.assertIn("duplicate charge", result.lower())
        self.assertEqual(fake_client.responses.kwargs["model"], "test-model")
        self.assertIn("Collect the transaction details", fake_client.responses.kwargs["input"])


if __name__ == "__main__":
    unittest.main()
