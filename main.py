"""Command-line entry point for the support automation tool."""

import argparse
from pathlib import Path

from app.pipeline import run_pipeline
from app.review import review_draft


DEFAULT_KB = Path(__file__).parent / "data" / "knowledge_base.json"


def _run_review(draft_response: str) -> None:
    """Interactively collect a human decision for the generated draft."""
    print("\nHuman review")
    print("[a] Approve  [e] Edit  [r] Reject")
    choice = input("Decision: ").strip().lower()

    actions = {"a": "approve", "e": "edit", "r": "reject"}
    if choice not in actions:
        print("Invalid decision. No response was approved or sent.")
        return

    edited_response = None
    if choice == "e":
        print("Enter the edited response. Finish with an empty line:")
        lines: list[str] = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        edited_response = "\n".join(lines)

    decision = review_draft(actions[choice], draft_response, edited_response)
    print(f"Review status: {decision.action}")
    if decision.response:
        print("\nFinal response for the support agent:\n")
        print(decision.response)
    else:
        print("The draft was rejected and will not be sent.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and draft support responses.")
    parser.add_argument("request", help="Incoming customer support request")
    parser.add_argument("--knowledge-base", default=DEFAULT_KB, type=Path)
    parser.add_argument(
        "--review",
        action="store_true",
        help="Open an interactive human-review step after drafting",
    )
    args = parser.parse_args()

    result = run_pipeline(args.request, args.knowledge_base)

    print(f"Category: {result.classification.category}")
    print(f"Confidence: {result.classification.confidence:.2f}")
    print("\nKnowledge base matches:")
    for match in result.matches:
        print(f"- {match.article.title} ({match.score:.4f})")
    print("\nDraft response:\n")
    print(result.draft.response)
    print("\nStatus: Awaiting human review")

    if args.review:
        _run_review(result.draft.response)


if __name__ == "__main__":
    main()
