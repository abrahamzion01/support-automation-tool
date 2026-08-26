
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from app.database import get_requests, initialize_database, save_request, update_request


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_result(self):
        return SimpleNamespace(
            request="I was charged twice.",
            classification=SimpleNamespace(
                category="billing",
                confidence=0.99,
            ),
            draft=SimpleNamespace(
                response="Original draft response",
                sources=["billing-duplicate-charge"],
            ),
        )

    def test_saved_request_starts_as_pending(self):
        request_id = save_request(
            self.make_result(),
            self.database_path,
        )

        rows = get_requests(self.database_path)

        self.assertEqual(rows[0][0], request_id)
        self.assertEqual(rows[0][5], '["billing-duplicate-charge"]')
        self.assertEqual(rows[0][6], "pending")

    def test_approve_updates_status(self):
        request_id = save_request(
            self.make_result(),
            self.database_path,
        )

        update_request(
            request_id,
            "approved",
            "Original draft response",
            self.database_path,
        )

        rows = get_requests(self.database_path)

        self.assertEqual(rows[0][6], "approved")
        self.assertEqual(rows[0][4], "Original draft response")

    def test_edit_updates_status_and_response(self):
        request_id = save_request(
            self.make_result(),
            self.database_path,
        )

        update_request(
            request_id,
            "edited",
            "Improved response",
            self.database_path,
        )

        rows = get_requests(self.database_path)

        self.assertEqual(rows[0][6], "edited")
        self.assertEqual(rows[0][4], "Improved response")

    def test_reject_updates_status_and_removes_response(self):
        request_id = save_request(
            self.make_result(),
            self.database_path,
        )

        update_request(
            request_id,
            "rejected",
            None,
            self.database_path,
        )

        rows = get_requests(self.database_path)

        self.assertEqual(rows[0][6], "rejected")
        self.assertIsNone(rows[0][4])


if __name__ == "__main__":
    unittest.main()
