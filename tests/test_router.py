import unittest

from app.router import route_message


class RouterTests(unittest.TestCase):
    def test_strong_support_request_routes_to_support(self):
        route = route_message("I was charged twice for my subscription")
        self.assertEqual(route.mode, "support")
        self.assertGreater(route.confidence, 0.65)

    def test_general_question_routes_to_general(self):
        route = route_message("Explain recursion like I am a beginner")
        self.assertEqual(route.mode, "general")
        self.assertGreater(route.confidence, 0.65)

    def test_programming_question_routes_to_general(self):
        route = route_message("What is the difference between Python and Go?")
        self.assertEqual(route.mode, "general")

    def test_unknown_message_defaults_to_general(self):
        route = route_message("Tell me something interesting")
        self.assertEqual(route.mode, "general")


if __name__ == "__main__":
    unittest.main()
