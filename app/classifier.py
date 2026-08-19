"""Deterministic, explainable support-request classification."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Classification:
    category: str
    confidence: float
    needs_review: bool = False
    matched_signals: tuple[str, ...] = ()


# Larger weights represent stronger evidence for a category. Phrases are
# intentionally included because real requests do not always use one exact
# keyword (for example, "money disappeared" is a billing signal).
SIGNALS = {
    "billing": {
        "strong": {
            "charged twice": 4,
            "charged me": 3,
            "duplicate charge": 4,
            "unknown transaction": 4,
            "money disappeared": 4,
            "billing": 2,
            "invoice": 2,
            "subscription": 2,
        },
        "keywords": {"bill", "charge", "charged", "payment", "invoice", "subscription", "price", "transaction"},
    },
    "technical": {
        "strong": {
            "not working": 4,
            "keeps crashing": 4,
            "cannot log in": 4,
            "can't log in": 4,
            "password reset": 3,
            "error message": 3,
        },
        "keywords": {"error", "bug", "broken", "crash", "failed", "failure", "login", "password", "technical"},
    },
    "account": {
        "strong": {
            "change my email": 4,
            "update my email": 4,
            "verify my account": 3,
            "account verification": 3,
        },
        "keywords": {"account", "profile", "email", "username", "verify", "verification"},
    },
    "shipping": {
        "strong": {
            "where is my order": 4,
            "where is my package": 4,
            "delivery date": 3,
            "track my order": 3,
        },
        "keywords": {"shipping", "delivery", "delivered", "package", "parcel", "order", "tracking", "carrier"},
    },
    "refund": {
        "strong": {
            "want a refund": 4,
            "request a refund": 4,
            "money back": 4,
            "get my money back": 4,
            "return an item": 3,
        },
        "keywords": {"refund", "refunded", "return", "reimbursement"},
    },
}

REVIEW_THRESHOLD = 0.65
AMBIGUITY_MARGIN = 0.15
MAX_CATEGORY_SCORE = 6


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _score_category(normalized: str, tokens: set[str], signals: dict) -> tuple[int, list[str]]:
    score = 0
    matched: list[str] = []

    for phrase, weight in signals["strong"].items():
        if phrase in normalized:
            score += weight
            matched.append(phrase)

    for keyword in signals["keywords"]:
        if keyword in tokens:
            score += 1
            matched.append(keyword)

    return score, matched


def classify_request(text: str) -> Classification:
    """Classify a request with weighted, transparent signals.

    Confidence reflects both the strength of the winning evidence and how
    clearly it beats competing categories. Weak matches are sent to review
    rather than being presented as highly confident classifications.
    """
    if not text or not text.strip():
        return Classification("unknown", 0.0, True, ())

    normalized = " ".join(text.lower().split())
    tokens = _tokens(normalized)
    scored: dict[str, tuple[int, list[str]]] = {}

    for category, signals in SIGNALS.items():
        score, matched = _score_category(normalized, tokens, signals)
        if score:
            scored[category] = (score, matched)

    if not scored:
        return Classification("unknown", 0.0, True, ())

    ranked = sorted(scored.items(), key=lambda item: item[1][0], reverse=True)
    category, (winning_score, matched) = ranked[0]
    total = sum(score for score, _ in scored.values())

    # Confidence combines absolute evidence strength with the share of the
    # evidence belonging to the winning category. This avoids treating a
    # single weak keyword as near-certain.
    strength = min(winning_score / MAX_CATEGORY_SCORE, 1.0)
    evidence_share = winning_score / max(total, 1)
    confidence = 0.5 + 0.3 * strength + 0.2 * evidence_share

    if len(ranked) > 1:
        second_score = ranked[1][1][0]
        gap = (winning_score - second_score) / max(total, 1)
    else:
        gap = 1.0

    needs_review = confidence < REVIEW_THRESHOLD or gap < AMBIGUITY_MARGIN
    return Classification(
        category=category,
        confidence=round(min(confidence, 0.99), 2),
        needs_review=needs_review,
        matched_signals=tuple(sorted(set(matched))),
    )
