"""Grounded response drafting for human review."""

from dataclasses import dataclass

from .ai import AIUnavailable, generate_grounded_draft
from .classifier import Classification
from .knowledge_base import SearchResult


@dataclass(frozen=True)
class Draft:
    response: str
    sources: list[str]
    confidence: float
    review_required: bool
    grounding_note: str
    ai_generated: bool = False


def _source_payload(results: list[SearchResult]) -> list[dict[str, str]]:
    return [
        {"id": r.article.id, "title": r.article.title, "content": r.article.content}
        for r in results
    ]


def draft_response(
    request: str,
    classification: Classification,
    results: list[SearchResult],
    use_ai: bool = True,
) -> Draft:
    """Create a grounded draft, using OpenAI when configured and falling back locally."""
    if not results:
        return Draft(
            "Hi,\n\nThanks for contacting support. I don't have enough verified information to answer this request yet. A support specialist should review it before a response is sent.\n\nBest,\nSupport Team",
            [], 0.0, True, "No knowledge-base article met the retrieval threshold.", False,
        )

    best = results[0]
    confidence = best.score
    review_required = classification.needs_review or confidence < 0.20
    sources = [r.article.id for r in results]

    if use_ai and not review_required:
        try:
            response = generate_grounded_draft(
                request,
                classification.category,
                _source_payload(results),
            )
            return Draft(
                response,
                sources,
                confidence,
                True,
                "AI-generated from retrieved knowledge. Strong grounding basis; human review is mandatory before approval.",
                True,
            )
        except AIUnavailable as exc:
            grounding_note = (
                "OpenAI unavailable; deterministic fallback used: "
                f"{exc}. Strong retrieved knowledge remains available for human review."
            )
    else:
        grounding_note = (
            "Deterministic draft used because AI was disabled or review is already required. "
            "Human review is required before approval."
        )

    response = (
        "Hi,\n\n"
        f"Thanks for contacting support about your {classification.category} request. "
        f"Based on our support guidance, {best.article.content}\n\n"
        "If you can provide the requested details, our support team can review the issue. "
        "Please do not send passwords or other sensitive credentials.\n\n"
        "Best,\nSupport Team"
    )
    return Draft(response, sources, confidence, review_required, grounding_note, False)
