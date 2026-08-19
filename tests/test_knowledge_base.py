import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).parents[1] / "data" / "knowledge_base.json"
        self.kb = KnowledgeBase.from_json(path)

    def test_search_returns_relevant_article(self):
        results = self.kb.search("I need help with a duplicate charge")
        self.assertTrue(results)
        self.assertEqual(results[0].article.id, "billing-duplicate-charge")

    def test_search_can_filter_by_category(self):
        results = self.kb.search("account email", category="account")
        self.assertTrue(results)
        self.assertTrue(all(result.article.category == "account" for result in results))
        self.assertEqual(results[0].article.id, "account-email")

    def test_min_score_filters_weak_matches(self):
        results = self.kb.search("I need help with an unrelated topic", min_score=0.9)
        self.assertEqual(results, [])

    def test_results_are_deterministically_ordered(self):
        first = self.kb.search("order support", limit=3)
        second = self.kb.search("order support", limit=3)
        self.assertEqual(first, second)

    def test_empty_query_returns_no_results(self):
        self.assertEqual(self.kb.search(""), [])

    def test_non_positive_limit_returns_no_results(self):
        self.assertEqual(self.kb.search("duplicate charge", limit=0), [])


if __name__ == "__main__":
    unittest.main()
