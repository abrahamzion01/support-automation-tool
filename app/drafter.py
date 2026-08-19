"""Grounded response drafting for human review."""

from dataclasses import dataclass

from .classifier import Classification
from .knowledge_base import SearchResult


@dataclass(frozen=True)
class Draft:
    response: str
    sources: list[str]


def draft_response(
    request: str,
    classification: Classification,
    results: list[SearchResult],
) -> Draft:
    """Create a transparent draft using only retrieved knowledge."""
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
        )

    best = results[0].article
    response = (
        "Hi,\n\n"
        f"Thanks for contacting support about your {classification.category} request. "
        f"Based on our support guidance, {best.content}\n\n"
        "If you can provide the requested details, our support team can review the issue. "
        "Please do not send passwords or other sensitive credentials.\n\n"
        "Best,\nSupport Team"
    )
    sources = [result.article.id for result in results]
    return Draft(response=response, sources=sources)
