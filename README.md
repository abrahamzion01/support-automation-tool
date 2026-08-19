# Support Automation Tool

A reproducible support automation pipeline that classifies incoming requests, searches a knowledge base, and drafts a clear response for human review.

## What the tool does

```text
Incoming request
      |
      v
+------------------+
| Classify request |
+--------+---------+
         |
         v
+------------------+
| Search knowledge |
| base              |
+--------+---------+
         |
         v
+------------------+
| Draft response   |
| + confidence     |
| + sources        |
+--------+---------+
         |
         v
+------------------+
| Human review     |
+----+------+------+ 
     |      |
  approve  edit/reject
```

The application is intentionally **human-in-the-loop**. It prepares a response but does not automatically send customer messages.

## Features

- Classifies support requests into practical categories.
- Uses explainable weighted signals and confidence scoring.
- Searches a local knowledge base with deterministic TF-IDF-style cosine similarity.
- Can restrict retrieval to the predicted category.
- Rejects weak retrieval matches instead of treating them as verified evidence.
- Drafts responses from retrieved knowledge rather than inventing unsupported guidance.
- Exposes draft confidence, source article IDs, and a grounding note for reviewers.
- Supports approve, edit, and reject decisions from the CLI.
- Handles unknown or ambiguous requests conservatively.
- Includes unit tests, end-to-end tests, and GitHub Actions CI.
- Uses only Python's standard library for the application runtime.

## Architecture

The core pipeline is split into small, testable components:

- `app/classifier.py` — turns an incoming request into a category, confidence score, matched signals, and review flag.
- `app/knowledge_base.py` — loads local JSON articles and ranks them with deterministic TF-IDF-style cosine similarity.
- `app/drafter.py` — creates a response only from retrieved knowledge and exposes grounding metadata.
- `app/pipeline.py` — orchestrates classification, retrieval, and drafting.
- `app/review.py` — validates the human's approve/edit/reject decision without sending anything externally.
- `main.py` — provides the command-line interface.

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
├── .github/
│   └── workflows/
│       └── tests.yml
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- No external API key
- No database
- No cloud service required for the baseline implementation

The application runtime uses only Python's standard library.

## Run locally

Clone the repository and enter it:

```bash
git clone https://github.com/abrahamzion01/support-automation-tool.git
cd support-automation-tool
```

Run a request through the pipeline:

```bash
python3 main.py "I was charged twice for my subscription"
```

You will see the classification, confidence, knowledge-base matches, draft grounding confidence, sources, and draft response.

To include interactive human review:

```bash
python3 main.py "I was charged twice for my subscription" --review
```

The reviewer can:

- `a` — approve the generated draft
- `e` — edit the draft before approval
- `r` — reject the draft

No action sends a message to a customer automatically.

## Run the tests

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover classification, retrieval, drafting, the end-to-end pipeline, and human review.

GitHub Actions runs the same unittest discovery command on pushes and pull requests using Python 3.11.

## Example

Input:

```text
I was charged twice for my subscription
```

The pipeline is expected to identify this as a billing request, retrieve the duplicate-charge guidance, and use that article as the grounding source for the draft.

A reviewer can then verify the source and either approve, edit, or reject the response.

## Safety and reliability decisions

### 1. Human approval is mandatory

The system generates drafts only. The review layer deliberately has no customer messaging integration.

### 2. Weak evidence is visible

Classification confidence and retrieval confidence are separate signals. An uncertain classification or weak knowledge match sets `review_required=True`.

### 3. Retrieval is deterministic

The baseline knowledge search runs locally and produces repeatable results from the same knowledge base and query. This makes behavior easier to test and reproduce.

### 4. Unknown requests are handled conservatively

If the classifier cannot find meaningful evidence, the category becomes `unknown` and the drafter tells the reviewer that verified information is unavailable instead of fabricating an answer.

### 5. Sources remain attached to drafts

Each draft records the IDs of the retrieved knowledge-base articles used to ground it. A human reviewer can therefore inspect the evidence behind the response.

## Engineering decisions I worked on

The main improvements in the current implementation are:

1. **Classifier confidence calibration** — confidence now considers evidence strength and ambiguity instead of treating a single weak keyword as highly certain.
2. **Safer retrieval** — knowledge-base search supports category filtering and minimum similarity thresholds, with deterministic result ordering.
3. **Grounded drafting** — drafts expose their confidence, sources, and review state so a human can distinguish strong evidence from uncertain matches.
4. **End-to-end verification** — tests now exercise the complete request → classification → retrieval → draft flow and the human review decisions.
5. **Reproducibility** — the baseline requires no external API keys or services and can be run locally with Python's standard library.

These are the areas I should be prepared to explain during a squad review: the reasoning behind the confidence calculation, how TF-IDF retrieval works, why weak matches require review, and how the tests prove that the components work together.

## Future improvements

Possible next steps include:

- replacing the baseline classifier with a trained or LLM-based classifier behind the existing interface;
- adding semantic/vector retrieval while keeping source tracking;
- adding a web/API interface for support agents;
- adding structured audit logs for review decisions;
- adding evaluation datasets and precision/recall metrics;
- adding authentication and role-based access before production deployment.
