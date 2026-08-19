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

    def test_no_results_require_review(self):
        draft = draft_response("Unknown", Classification("unknown", 0.0), [])
        self.assertIn("support specialist", draft.response)
        self.assertEqual(draft.sources, [])


if __name__ == "__main__":
    unittest.main()
