"""Grounded response drafting for human review."""

from dataclasses import dataclass

from .classifier import Classification
from .knowledge_base import SearchResult


@dataclass(frozen=True)
class Draft:
    response: str
    sources: list[str]
    confidence: float
    review_required: bool
    grounding_note: str


def draft_response(
    request: str,
    classification: Classification,
    results: list[SearchResult],
) -> Draft:
    """Create a transparent draft using only retrieved knowledge.

    The draft deliberately exposes retrieval confidence and review state so a
    human can distinguish verified guidance from an uncertain match.
    """
    if not results:
        return Draft(
            response=(
                "Hi,\n\n"
                "Thanks for contacting support. I don't have enough verified "
                "information to answer this request yet. A support specialist "
                "should review it before a response is sent.\n\n"
                "Best,\nSupport Team"
            ),
            sources=[],
            confidence=0.0,
            review_required=True,
            grounding_note="No knowledge-base article met the retrieval threshold.",
        )

    best = results[0]
    confidence = best.score
    review_required = classification.needs_review or confidence < 0.20
    review_note = (
        "Human review is required because the classification or knowledge match is uncertain."
        if review_required
        else "Retrieved guidance provides a strong basis for human review."
    )

    response = (
        "Hi,\n\n"
        f"Thanks for contacting support about your {classification.category} request. "
        f"Based on our support guidance, {best.article.content}\n\n"
        "If you can provide the requested details, our support team can review the issue. "
        "Please do not send passwords or other sensitive credentials.\n\n"
        "Best,\nSupport Team"
    )
    sources = [result.article.id for result in results]
    return Draft(
        response=response,
        sources=sources,
        confidence=confidence,
        review_required=review_required,
        grounding_note=review_note,
    )
