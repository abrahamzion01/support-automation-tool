import unittest
from pathlib import Path
from unittest.mock import patch

from app.web import create_app


KB_PATH = Path(__file__).parents[1] / "data" / "knowledge_base.json"


class WebTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(KB_PATH)
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Support Automation AI", response.data)

    def test_empty_request_is_rejected(self):
        response = self.client.post("/support", data={"message": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please enter a support request", response.data)

    def test_support_request_reaches_review_page(self):
        response = self.client.post(
            "/support",
            data={"message": "I was charged twice for my subscription."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Human Review", response.data)
        self.assertIn(b"billing-duplicate-charge", response.data)

    def test_history_page_loads(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Request History", response.data)
        self.assertIn(b"No requests yet", response.data)

    def test_submitted_request_appears_in_history(self):
        response = self.client.post(
            "/support",
            data={"message": "I was charged twice for my subscription."},
        )
        self.assertEqual(response.status_code, 200)

        history = self.client.get("/history")
        self.assertEqual(history.status_code, 200)
        self.assertIn(b"I was charged twice for my subscription.", history.data)
        self.assertIn(b"billing-duplicate-charge", history.data)

    @patch("app.web.run_pipeline")
    def test_approve_review(self, run_pipeline):
        result = __import__("app.pipeline", fromlist=["SupportResult"]).run_pipeline(
            "I was charged twice for my subscription.", KB_PATH
        )
        run_pipeline.return_value = result

        response = self.client.post("/support", data={"message": "duplicate charge"})
        self.assertEqual(response.status_code, 200)

        decision = self.client.post("/review/1", data={"action": "approve"})
        self.assertEqual(decision.status_code, 200)
        self.assertIn(b"Review approved", decision.data)


if __name__ == "__main__":
    unittest.main()
