"""Small in-memory conversation history for multi-turn AI responses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class Conversation:
    def __init__(self, max_messages: int = 12):
        if max_messages < 2:
            raise ValueError("max_messages must be at least 2")
        self.max_messages = max_messages
        self._messages: list[Message] = []

    def add(self, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")
        if not content.strip():
            raise ValueError("message content cannot be empty")
        self._messages.append(Message(role, content.strip()))
        self._messages = self._messages[-self.max_messages :]

    def history(self) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
