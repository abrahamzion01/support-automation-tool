"""Unified conversational entry point."""

from dataclasses import dataclass
from pathlib import Path

from .ai import AIUnavailable, generate_general_response
from .conversation import Conversation
from .pipeline import run_pipeline
from .router import Route, route_message


@dataclass(frozen=True)
class ChatResult:
    route: Route
    response: str
    ai_used: bool
    support_result: object | None = None


def chat(
    message: str,
    conversation: Conversation,
    knowledge_base_path: str | Path,
) -> ChatResult:
    """Route a message, answer it, and retain the conversation turn."""
    route = route_message(message)

    if route.mode == "support":
        support_result = run_pipeline(message, knowledge_base_path)
        response = support_result.draft.response
        result = ChatResult(route, response, support_result.draft.ai_generated, support_result)
    else:
        try:
            response = generate_general_response(message, conversation.history())
            ai_used = True
        except AIUnavailable:
            response = (
                "I can help with general questions, but the AI service is currently "
                "unavailable. Please try again later."
            )
            ai_used = False
        result = ChatResult(route, response, ai_used)

    conversation.add("user", message)
    conversation.add("assistant", response)
    return result
