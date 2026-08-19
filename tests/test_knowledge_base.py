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

    def test_empty_query_returns_no_results(self):
        self.assertEqual(self.kb.search(""), [])


if __name__ == "__main__":
    unittest.main()
