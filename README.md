# Support Automation Tool

A reproducible support automation pipeline that classifies incoming requests, searches a knowledge base, and drafts a clear response for human review.

## Features

- Classifies support requests into practical categories.
- Searches a local knowledge base using deterministic TF-IDF-style retrieval.
- Drafts responses grounded in retrieved articles.
- Keeps a human in the loop: drafts are never sent automatically.
- Supports approve, edit, and reject review decisions from the CLI.
- Includes automated tests and GitHub Actions CI.
- Uses only Python's standard library for the application runtime.

## Architecture

```text
Incoming request
      |
      v
Request classifier
      |
      v
Knowledge-base search
      |
      v
Response drafter
      |
      v
Human review
   /   |   \
approve edit reject
```

## Project structure

```text
support-automation-tool/
├── app/
│   ├── classifier.py
│   ├── drafter.py
│   ├── knowledge_base.py
│   ├── pipeline.py
│   └── review.py
├── data/
│   └── knowledge_base.json
├── tests/
│   ├── test_classifier.py
│   ├── test_drafter.py
│   ├── test_knowledge_base.py
│   ├── test_pipeline.py
│   └── test_review.py
├── .github/workflows/tests.yml
├── main.py
├── requirements.txt
└── README.md
```

## Run locally

Requires Python 3.11+.

Run the pipeline without interactive review:

```bash
python3 main.py "I was charged twice for my subscription"
```

Run the pipeline and open the human-review step:

```bash
python3 main.py "I was charged twice for my subscription" --review
```

The reviewer can approve the draft, edit it, or reject it. The tool never sends a customer message automatically.

Run tests with:

```bash
python3 -m unittest discover -s tests -v
```

No API key or external service is required for the baseline implementation.

## Development approach

The baseline implementation is intentionally deterministic and reproducible. A future LLM integration can replace the classifier or drafter behind the same interfaces without changing the knowledge-base or review workflow.
