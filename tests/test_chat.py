import unittest
from pathlib import Path
from unittest.mock import patch

from app.chat import chat
from app.conversation import Conversation


KB_PATH = Path(__file__).parents[1] / "data" / "knowledge_base.json"


class ChatTests(unittest.TestCase):
    @patch("app.chat.generate_general_response")
    def test_general_chat_uses_ai_and_remembers_turn(self, generate):
        generate.return_value = "Recursion is when a function calls itself."
        conversation = Conversation()

        result = chat("Explain recursion", conversation, KB_PATH)

        self.assertEqual(result.route.mode, "general")
        self.assertTrue(result.ai_used)
        self.assertEqual(result.response, generate.return_value)
        self.assertEqual(conversation.history()[0].content, "Explain recursion")
        self.assertEqual(conversation.history()[1].role, "assistant")
        generate.assert_called_once()

    @patch("app.chat.generate_general_response")
    def test_general_chat_receives_previous_history(self, generate):
        generate.return_value = "Go uses static typing."
        conversation = Conversation()
        conversation.add("user", "What is Go?")
        conversation.add("assistant", "Go is a programming language.")

        chat("Does it use static typing?", conversation, KB_PATH)

        history = generate.call_args.args[1]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "What is Go?")

    @patch("app.chat.generate_general_response")
    def test_support_chat_uses_support_pipeline(self, generate):
        result = chat("I was charged twice for my subscription", Conversation(), KB_PATH)

        self.assertEqual(result.route.mode, "support")
        self.assertIsNotNone(result.support_result)
        generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
