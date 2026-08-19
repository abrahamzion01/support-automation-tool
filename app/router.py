"""Route messages between support and general conversational modes."""

from dataclasses import dataclass
import re

from .classifier import classify_request


@dataclass(frozen=True)
class Route:
    mode: str
    confidence: float
    reason: str


GENERAL_SIGNALS = {
    "what is", "what are", "how does", "how do", "explain", "teach me",
    "difference between", "meaning of", "define", "write code", "programming",
    "python", "javascript", "golang", "go language", "math", "history",
}


def route_message(message: str) -> Route:
    """Choose support or general mode using explicit, conservative signals."""
    text = " ".join(message.lower().split())
    if not text:
        return Route("general", 0.0, "Empty message; general mode can handle the conversation.")

    support = classify_request(message)
    if support.category != "unknown" and not support.needs_review:
        return Route("support", support.confidence, "Strong support classification matched.")

    matched_general = [signal for signal in GENERAL_SIGNALS if signal in text]
    if matched_general:
        confidence = min(0.95, 0.65 + 0.05 * len(matched_general))
        return Route("general", confidence, "General conversational signal matched.")

    if support.category != "unknown":
        return Route("support", support.confidence, "Support signal exists but requires human review.")

    return Route("general", 0.55, "No strong support signal; treat as a general conversation.")
