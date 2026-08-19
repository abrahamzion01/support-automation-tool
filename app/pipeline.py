"""End-to-end support automation pipeline."""

from dataclasses import dataclass
from pathlib import Path

from .classifier import Classification, classify_request
from .drafter import Draft, draft_response
from .knowledge_base import KnowledgeBase, SearchResult


@dataclass(frozen=True)
class SupportResult:
    request: str
    classification: Classification
    matches: list[SearchResult]
    draft: Draft


def run_pipeline(request: str, knowledge_base_path: str | Path) -> SupportResult:
    """Classify, retrieve supporting knowledge, and draft for human review."""
    classification = classify_request(request)

    # An uncertain classification should never be hidden from the reviewer.
    # Retrieval still runs because relevant knowledge can help the human make
    # the final decision.
    knowledge_base = KnowledgeBase.from_json(knowledge_base_path)
    matches = knowledge_base.search(request, limit=3)
    draft = draft_response(request, classification, matches)
    return SupportResult(request, classification, matches, draft)
