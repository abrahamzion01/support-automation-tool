import unittest

from app.review import review_draft


class ReviewTests(unittest.TestCase):
    def test_approve_keeps_generated_response(self):
        decision = review_draft("approve", "Draft response")
        self.assertEqual(decision.action, "approved")
        self.assertEqual(decision.response, "Draft response")

    def test_edit_requires_replacement_text(self):
        with self.assertRaises(ValueError):
            review_draft("edit", "Draft response")

    def test_edit_returns_edited_response(self):
        decision = review_draft("edit", "Draft response", "Improved response")
        self.assertEqual(decision.action, "edited")
        self.assertEqual(decision.response, "Improved response")

    def test_reject_removes_response(self):
        decision = review_draft("reject", "Draft response")
        self.assertEqual(decision.action, "rejected")
        self.assertIsNone(decision.response)

    def test_invalid_action_is_rejected(self):
        with self.assertRaises(ValueError):
            review_draft("send", "Draft response")


if __name__ == "__main__":
    unittest.main()
