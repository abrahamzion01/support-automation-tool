import unittest

from app.classifier import classify_request


class ClassifierTests(unittest.TestCase):
    def test_billing_request(self):
        result = classify_request("I was charged twice for my subscription")
        self.assertEqual(result.category, "billing")
        self.assertGreater(result.confidence, 0.5)
        self.assertFalse(result.needs_review)
        self.assertIn("charged twice", result.matched_signals)

    def test_paraphrased_billing_request(self):
        result = classify_request("Money disappeared from my account and I don't recognize the transaction")
        self.assertEqual(result.category, "billing")
        self.assertIn("money disappeared", result.matched_signals)

    def test_phrase_based_technical_request(self):
        result = classify_request("My app keeps crashing whenever I open it")
        self.assertEqual(result.category, "technical")
        self.assertIn("keeps crashing", result.matched_signals)

    def test_refund_phrase(self):
        result = classify_request("I want to get my money back for this order")
        self.assertEqual(result.category, "refund")
        self.assertIn("get my money back", result.matched_signals)

    def test_single_weak_signal_requires_review(self):
        result = classify_request("I have a question about my account")
        self.assertEqual(result.category, "account")
        self.assertLess(result.confidence, 0.65)
        self.assertTrue(result.needs_review)

    def test_unknown_request_requires_review(self):
        result = classify_request("Tell me something completely unrelated")
        self.assertEqual(result.category, "unknown")
        self.assertEqual(result.confidence, 0.0)
        self.assertTrue(result.needs_review)

    def test_empty_request_requires_review(self):
        result = classify_request("")
        self.assertEqual(result.category, "unknown")
        self.assertTrue(result.needs_review)


if __name__ == "__main__":
    unittest.main()
