"""Command-line entry point for the support automation tool."""

import argparse
from pathlib import Path

from app.pipeline import run_pipeline


DEFAULT_KB = Path(__file__).parent / "data" / "knowledge_base.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and draft support responses.")
    parser.add_argument("request", help="Incoming customer support request")
    parser.add_argument("--knowledge-base", default=DEFAULT_KB, type=Path)
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


if __name__ == "__main__":
    main()
