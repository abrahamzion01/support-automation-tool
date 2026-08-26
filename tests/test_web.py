import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.web import create_app


KB_PATH = Path(__file__).parents[1] / "data" / "knowledge_base.json"


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.app = create_app(KB_PATH, database_path=self.db_path)
        self.app.config.update(TESTING=True)

        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Support Automation AI", response.data)

    def test_empty_request_is_rejected(self):
        response = self.client.post(
            "/support",
            data={"message": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b"Please enter a support request",
            response.data,
        )

    def test_support_request_reaches_review_page(self):
        response = self.client.post(
            "/support",
            data={
                "message": "I was charged twice for my subscription.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Human Review", response.data)
        self.assertIn(b"billing-duplicate-charge", response.data)

    def test_history_page_loads(self):
        response = self.client.get("/history")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Request History", response.data)
        self.assertIn(b"No requests yet", response.data)

    def submit_support_request(self):
        response = self.client.post(
            "/support",
            data={
                "message": "I was charged twice for my subscription.",
            },
        )
        self.assertEqual(response.status_code, 200)

    @patch("app.web.run_pipeline")
    def test_submitted_request_appears_in_history(self, run_pipeline):
        result = __import__(
            "app.pipeline",
            fromlist=["SupportResult"],
        ).run_pipeline(
            "I was charged twice for my subscription.",
            KB_PATH,
        )
        run_pipeline.return_value = result

        self.submit_support_request()

        history = self.client.get("/history")

        self.assertEqual(history.status_code, 200)
        self.assertIn(
            b"I was charged twice for my subscription.",
            history.data,
        )
        self.assertIn(b"billing-duplicate-charge", history.data)
        self.assertIn(b"pending", history.data)

    def make_pipeline_result(self):
        return __import__(
            "app.pipeline",
            fromlist=["SupportResult"],
        ).run_pipeline(
            "I was charged twice for my subscription.",
            KB_PATH,
        )

    @patch("app.web.run_pipeline")
    def test_approve_review_persists_decision(self, run_pipeline):
        run_pipeline.return_value = self.make_pipeline_result()
        self.submit_support_request()

        decision = self.client.post(
            "/review/1",
            data={"action": "approve"},
        )

        self.assertEqual(decision.status_code, 200)
        self.assertIn(b"Review approved", decision.data)

        history = self.client.get("/history")
        self.assertIn(b"approved", history.data)

    @patch("app.web.run_pipeline")
    def test_edit_review_persists_decision(self, run_pipeline):
        run_pipeline.return_value = self.make_pipeline_result()
        self.submit_support_request()

        decision = self.client.post(
            "/review/1",
            data={
                "action": "edit",
                "edited_response": "Improved response for the customer.",
            },
        )

        self.assertEqual(decision.status_code, 200)
        self.assertIn(b"Review edited", decision.data)

        history = self.client.get("/history")
        self.assertIn(b"edited", history.data)
        self.assertIn(
            b"Improved response for the customer.",
            history.data,
        )

    @patch("app.web.run_pipeline")
    def test_reject_review_persists_decision(self, run_pipeline):
        run_pipeline.return_value = self.make_pipeline_result()
        self.submit_support_request()

        decision = self.client.post(
            "/review/1",
            data={"action": "reject"},
        )

        self.assertEqual(decision.status_code, 200)
        self.assertIn(b"Review rejected", decision.data)

        history = self.client.get("/history")
        self.assertIn(b"rejected", history.data)


if __name__ == "__main__":
    unittest.main()
