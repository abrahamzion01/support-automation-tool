import unittest
from pathlib import Path

from app.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_returns_human_review_draft(self):
        path = Path(__file__).parents[1] / "data" / "knowledge_base.json"
        result = run_pipeline("I was charged twice for my subscription", path)

        self.assertEqual(result.classification.category, "billing")
        self.assertTrue(result.matches)
        self.assertTrue(result.draft.sources)
        self.assertIn("Support Team", result.draft.response)


if __name__ == "__main__":
    unittest.main()
