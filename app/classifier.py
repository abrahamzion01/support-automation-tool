"""Deterministic support-request classification."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Classification:
    category: str
    confidence: float


KEYWORDS = {
    "billing": {"bill", "billing", "charge", "charged", "payment", "invoice", "subscription", "price"},
    "technical": {"error", "bug", "broken", "crash", "failed", "failure", "login", "password", "not working"},
    "account": {"account", "profile", "email", "username", "verify", "verification"},
    "shipping": {"shipping", "delivery", "delivered", "package", "parcel", "order", "tracking"},
    "refund": {"refund", "refunded", "money back", "return"},
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def classify_request(text: str) -> Classification:
    """Classify a request using transparent keyword scoring.

    Confidence is based on the winning category's share of all matching
    category keywords, with a small floor for weak matches.
    """
    if not text or not text.strip():
        return Classification("unknown", 0.0)

    normalized = text.lower()
    tokens = _tokens(normalized)
    scores: dict[str, int] = {}

    for category, keywords in KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in tokens or keyword in normalized)
        if score:
            scores[category] = score

    if not scores:
        return Classification("unknown", 0.0)

    category, winning_score = max(scores.items(), key=lambda item: item[1])
    total = sum(scores.values())
    confidence = min(0.99, 0.50 + 0.50 * (winning_score / total))
    return Classification(category, round(confidence, 2))
