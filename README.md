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
+-----------------------------+
| AI / deterministic drafting |
| + confidence + sources      |
+-------------+---------------+
              |
              v
      +----------------+
      | Human review   |
      +---+---------+--+
          |         |
       approve   edit/reject
```

The application is intentionally **human-in-the-loop**. It prepares a response but does not automatically send customer messages.

## Features

- Classifies support requests into practical categories.
- Uses explainable weighted signals and confidence scoring.
- Searches a local knowledge base with deterministic TF-IDF-style cosine similarity.
- Can restrict retrieval to the predicted category.
- Rejects weak retrieval matches instead of treating them as verified evidence.
- Uses OpenAI for more natural, context-aware drafts when configured.
- Grounds AI drafts in retrieved knowledge-base material.
- Falls back to the deterministic drafter when OpenAI is unavailable.
- Exposes draft confidence, source article IDs, AI status, and a grounding note for reviewers.
- Supports approve, edit, and reject decisions from the CLI.
- Handles unknown or ambiguous requests conservatively.
- Includes unit tests, mocked AI tests, end-to-end tests, and GitHub Actions CI.

## Architecture

The core pipeline is split into small, testable components:

- `app/classifier.py` — turns an incoming request into a category, confidence score, matched signals, and review flag.
- `app/knowledge_base.py` — loads local JSON articles and ranks them with deterministic TF-IDF-style cosine similarity.
- `app/ai.py` — integrates the OpenAI Responses API and isolates API failures behind `AIUnavailable`.
- `app/drafter.py` — chooses an AI-grounded draft when appropriate and falls back to the deterministic draft when needed.
- `app/pipeline.py` — orchestrates classification, retrieval, and drafting.
- `app/review.py` — validates the human's approve/edit/reject decision without sending anything externally.
- `main.py` — provides the command-line interface.

## Project structure

```text
support-automation-tool/
├── app/
│   ├── ai.py
│   ├── classifier.py
│   ├── drafter.py
│   ├── knowledge_base.py
│   ├── pipeline.py
│   └── review.py
├── data/
│   └── knowledge_base.json
├── tests/
│   ├── test_ai.py
│   ├── test_classifier.py
│   ├── test_drafter.py
│   ├── test_knowledge_base.py
│   ├── test_pipeline.py
│   └── test_review.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- An OpenAI API key for AI-powered drafting
- No database
- No cloud service is required when using the deterministic fallback

The application uses the official OpenAI Python SDK when AI drafting is enabled. The OpenAI API uses the Responses API for direct model requests. citeturn0search0

## Configure OpenAI

Create a local environment file from the example:

```bash
cp .env.example .env
```

Then set your API key:

```text
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-5.6-luna
```

**Never commit `.env` or a real API key.** The repository's `.gitignore` excludes `.env`.

The default model is `gpt-5.6-luna`, which OpenAI currently describes as optimized for cost-sensitive, high-volume workloads. citeturn0search0

If no API key is configured, the application automatically uses the deterministic local drafter instead.

## Run locally

Clone the repository and enter it:

```bash
git clone https://github.com/abrahamzion01/support-automation-tool.git
cd support-automation-tool
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run a request through the pipeline:

```bash
python3 main.py "I was charged twice for my subscription"
```

The CLI displays:

- classification and confidence;
- knowledge-base matches;
- draft grounding confidence;
- whether OpenAI generated the draft;
- the knowledge sources used;
- the grounding/review note;
- the draft response.

To include interactive human review:

```bash
python3 main.py "I was charged twice for my subscription" --review
```

The reviewer can:

- `a` — approve the generated draft;
- `e` — edit the draft before approval;
- `r` — reject the draft.

No action sends a message to a customer automatically.

## Run the tests

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover classification, retrieval, drafting, the OpenAI integration without making real API calls, the end-to-end pipeline, and human review.

GitHub Actions runs the unittest suite on pushes and pull requests. CI does not need an OpenAI API key because the AI integration is mocked in tests.

## Example

Input:

```text
I was charged twice for my subscription
```

The pipeline identifies this as a billing request, retrieves the duplicate-charge guidance, and — when OpenAI is configured and the evidence is sufficiently strong — asks the model to turn that verified material into a professional draft.

The AI receives the customer request, category, and retrieved knowledge-base material. It is explicitly instructed to use only that material and not invent policies, prices, timelines, guarantees, or credentials. The draft remains subject to human review.

## AI safety and reliability

### 1. Human approval is mandatory

The system generates drafts only. The review layer deliberately has no customer messaging integration.

### 2. Retrieval remains the source of truth

OpenAI receives retrieved knowledge rather than being allowed to answer from general knowledge. This keeps support guidance tied to the application's knowledge base.

### 3. AI failure does not break the application

Missing API keys, missing SDKs, API failures, and empty model responses are handled as `AIUnavailable`. The drafter then uses the deterministic local response path.

### 4. Weak evidence is visible

Classification confidence and retrieval confidence are separate signals. An uncertain classification or weak knowledge match sets `review_required=True`.

### 5. AI-generated drafts are explicitly marked

The `Draft` object contains `ai_generated`, so downstream code and the CLI can distinguish an AI response from a deterministic fallback.

### 6. Secrets stay out of source control

API credentials are loaded from `OPENAI_API_KEY` and `.env` is ignored by Git. No secret is stored in the repository.

## Engineering decisions I worked on

The main improvements in the current implementation are:

1. **Classifier confidence calibration** — confidence considers evidence strength and ambiguity instead of treating a single weak keyword as highly certain.
2. **Safer retrieval** — knowledge-base search supports category filtering and minimum similarity thresholds, with deterministic result ordering.
3. **Grounded drafting** — drafts expose confidence, sources, and review state so a human can distinguish strong evidence from uncertain matches.
4. **OpenAI integration** — the AI layer is isolated in `app/ai.py`, uses the Responses API, accepts configuration through environment variables, and has a deterministic fallback.
5. **End-to-end verification** — tests exercise the request → classification → retrieval → draft flow, including mocked AI behavior and human review decisions.
6. **Reproducibility** — CI tests the application without requiring an OpenAI API key or live external model calls.

These are the areas to be prepared to explain during a squad review: the reasoning behind the confidence calculation, how TF-IDF retrieval works, how retrieved context is passed to OpenAI, why weak matches require review, how the fallback works, and how the tests prove the system behaves safely.

## Future improvements

Possible next steps include:

- AI-assisted classification with structured output and deterministic fallback;
- semantic/vector retrieval while keeping source tracking;
- a web/API interface for support agents;
- structured audit logs for review decisions;
- evaluation datasets and precision/recall/groundedness metrics;
- rate limiting and cost controls for AI usage;
- authentication and role-based access before production deployment.
