import unittest
from pathlib import Path

from app.pipeline import run_pipeline


KB_PATH = Path(__file__).parents[1] / "data" / "knowledge_base.json"


class PipelineTests(unittest.TestCase):
    def test_billing_request_is_classified_retrieved_and_drafted(self):
        result = run_pipeline("I was charged twice for my subscription", KB_PATH)

        self.assertEqual(result.classification.category, "billing")
        self.assertGreater(result.classification.confidence, 0.65)
        self.assertTrue(result.matches)
        self.assertEqual(result.matches[0].article.id, "billing-duplicate-charge")
        self.assertIn("duplicate", result.draft.response.lower())
        self.assertIn("billing-duplicate-charge", result.draft.sources)
        self.assertGreater(result.draft.confidence, 0.0)

    def test_unknown_request_is_safe_and_requires_review(self):
        result = run_pipeline("Can you tell me something completely unrelated?", KB_PATH)

        self.assertEqual(result.classification.category, "unknown")
        self.assertTrue(result.classification.needs_review)
        self.assertTrue(result.draft.review_required)
        self.assertEqual(result.draft.sources, [])
        self.assertIn("don't have enough verified information", result.draft.response)

    def test_weak_request_does_not_claim_high_confidence(self):
        result = run_pipeline("I have a question about my account", KB_PATH)

        self.assertEqual(result.classification.category, "account")
        self.assertTrue(result.classification.needs_review)
        self.assertTrue(result.draft.review_required)


if __name__ == "__main__":
    unittest.main()
