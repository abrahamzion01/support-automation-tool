import unittest

from app.classifier import Classification
from app.drafter import draft_response
from app.knowledge_base import Article, SearchResult


class DrafterTests(unittest.TestCase):
    def test_draft_uses_retrieved_source(self):
        article = Article(
            id="refund-request",
            title="Refund requests",
            category="refund",
            content="Collect the order number before reviewing refund eligibility.",
        )
        draft = draft_response(
            "I want a refund",
            Classification("refund", 0.9),
            [SearchResult(article, 0.8)],
        )
        self.assertIn("Collect the order number", draft.response)
        self.assertEqual(draft.sources, ["refund-request"])
        self.assertEqual(draft.confidence, 0.8)
        self.assertFalse(draft.review_required)
        self.assertIn("strong basis", draft.grounding_note)

    def test_uncertain_classification_requires_review(self):
        article = Article(
            id="account-email",
            title="Changing an account email",
            category="account",
            content="Verify the account before changing the email.",
        )
        draft = draft_response(
            "I have an account question",
            Classification("account", 0.55, True),
            [SearchResult(article, 0.8)],
        )
        self.assertTrue(draft.review_required)
        self.assertIn("Human review", draft.grounding_note)

    def test_weak_retrieval_requires_review(self):
        article = Article(
            id="technical-error",
            title="Unexpected errors",
            category="technical",
            content="Collect the error message and device details.",
        )
        draft = draft_response(
            "Something is wrong",
            Classification("technical", 0.9),
            [SearchResult(article, 0.12)],
        )
        self.assertTrue(draft.review_required)
        self.assertEqual(draft.confidence, 0.12)

    def test_no_results_require_review(self):
        draft = draft_response("Unknown", Classification("unknown", 0.0, True), [])
        self.assertIn("support specialist", draft.response)
        self.assertEqual(draft.sources, [])
        self.assertEqual(draft.confidence, 0.0)
        self.assertTrue(draft.review_required)
        self.assertIn("No knowledge-base article", draft.grounding_note)


if __name__ == "__main__":
    unittest.main()
