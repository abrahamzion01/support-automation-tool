import unittest

from app.classifier import classify_request


class ClassifierTests(unittest.TestCase):
    def test_billing_request(self):
        result = classify_request("I was charged twice for my subscription")
        self.assertEqual(result.category, "billing")
        self.assertGreater(result.confidence, 0.5)

    def test_unknown_request(self):
        result = classify_request("Tell me something completely unrelated")
        self.assertEqual(result.category, "unknown")
        self.assertEqual(result.confidence, 0.0)

    def test_empty_request(self):
        self.assertEqual(classify_request("" ).category, "unknown")


if __name__ == "__main__":
    unittest.main()
