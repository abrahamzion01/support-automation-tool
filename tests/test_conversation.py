import unittest

from app.conversation import Conversation


class ConversationTests(unittest.TestCase):
    def test_history_is_bounded(self):
        conversation = Conversation(max_messages=2)
        conversation.add("user", "first")
        conversation.add("assistant", "second")
        conversation.add("user", "third")

        self.assertEqual(
            conversation.history(),
            [
                conversation.history()[0],
                conversation.history()[1],
            ],
        )
        self.assertEqual(conversation.history()[0].content, "second")
        self.assertEqual(conversation.history()[1].content, "third")

    def test_invalid_role_is_rejected(self):
        conversation = Conversation()
        with self.assertRaises(ValueError):
            conversation.add("system", "not allowed")

    def test_empty_content_is_rejected(self):
        conversation = Conversation()
        with self.assertRaises(ValueError):
            conversation.add("user", "   ")

    def test_clear_removes_history(self):
        conversation = Conversation()
        conversation.add("user", "hello")
        conversation.clear()
        self.assertEqual(conversation.history(), [])


if __name__ == "__main__":
    unittest.main()
