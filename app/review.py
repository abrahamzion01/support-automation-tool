"""Human review decisions for generated support drafts."""

from dataclasses import dataclass


VALID_ACTIONS = {"approve", "edit", "reject"}


@dataclass(frozen=True)
class ReviewDecision:
    action: str
    response: str | None


def review_draft(action: str, draft_response: str, edited_response: str | None = None) -> ReviewDecision:
    """Validate and record a human decision without sending the response."""
    action = action.strip().lower()
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid review action: {action}")

    if action == "approve":
        return ReviewDecision(action="approved", response=draft_response)

    if action == "edit":
        if not edited_response or not edited_response.strip():
            raise ValueError("An edited response is required when choosing edit")
        return ReviewDecision(action="edited", response=edited_response.strip())

    return ReviewDecision(action="rejected", response=None)
