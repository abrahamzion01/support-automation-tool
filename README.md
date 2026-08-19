# Support Automation Tool

A reproducible AI-assisted support automation tool that can handle company-specific support requests, answer general questions conversationally, search a knowledge base, and prepare responses for human review.

## What the tool does

```text
                         User message
                              |
                              v
                       +--------------+
                       | AI Router    |
                       +------+-------+
                              |
                +-------------+-------------+
                |                           |
                v                           v
         Support request              General question
                |                           |
                v                           v
        Classifier + KB              OpenAI conversation
                |                           |
                v                           |
         Grounded AI draft                 |
                |                           |
                +-------------+-------------+
                              v
                       Human review
                    approve / edit / reject
```

The application is intentionally **human-in-the-loop** for support responses. It prepares a response but does not automatically send customer messages.

## Features

- Routes messages between support and general conversational modes.
- Classifies support requests with explainable weighted signals and confidence scoring.
- Searches a local knowledge base with deterministic TF-IDF-style cosine similarity.
- Restricts support retrieval to the predicted category when appropriate.
- Rejects weak retrieval matches instead of treating them as verified evidence.
- Uses OpenAI for natural, context-aware responses when configured.
- Grounds support AI drafts in retrieved knowledge-base material.
- Falls back to a deterministic local support drafter when OpenAI is unavailable.
- Maintains bounded multi-turn conversation history for general AI conversations.
- Exposes draft confidence, source IDs, AI status, and grounding notes for reviewers.
- Supports approve, edit, and reject decisions for support drafts.
- Includes unit tests, mocked AI tests, end-to-end tests, and GitHub Actions CI.

## Architecture

The main components are:

- `app/router.py` — chooses `support` or `general` mode.
- `app/conversation.py` — stores a bounded history of user/assistant turns.
- `app/chat.py` — unified entry point that routes a message and updates conversation history.
- `app/classifier.py` — classifies support requests and estimates confidence.
- `app/knowledge_base.py` — loads local JSON articles and ranks them with deterministic TF-IDF-style cosine similarity.
- `app/ai.py` — integrates the OpenAI Responses API for grounded support drafts and general conversation.
- `app/drafter.py` — generates AI-grounded support drafts when appropriate and falls back locally.
- `app/pipeline.py` — orchestrates support classification, retrieval, and drafting.
- `app/review.py` — validates approve/edit/reject decisions without sending anything externally.
- `main.py` — command-line interface for single requests and multi-turn chat.

## Project structure

```text
support-automation-tool/
├── app/
│   ├── ai.py
│   ├── chat.py
│   ├── classifier.py
│   ├── conversation.py
│   ├── drafter.py
│   ├── knowledge_base.py
│   ├── pipeline.py
│   ├── review.py
│   └── router.py
├── data/
│   └── knowledge_base.json
├── tests/
│   ├── test_ai.py
│   ├── test_chat.py
│   ├── test_classifier.py
│   ├── test_conversation.py
│   ├── test_drafter.py
│   ├── test_knowledge_base.py
│   ├── test_pipeline.py
│   ├── test_review.py
│   └── test_router.py
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
- An OpenAI API key for AI-powered responses
- No database required
- No cloud service required when using the deterministic support fallback

The application uses the official OpenAI Python SDK when AI features are enabled.

## Configure OpenAI

Create a local environment file from the example:

```bash
cp .env.example .env
```

Set your API key in `.env`:

```text
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-5.6-luna
```

**Never commit `.env` or a real API key.** The repository's `.gitignore` excludes `.env`.

If no API key is configured, company-specific support requests continue to work through the deterministic local path. General conversations report that the AI service is unavailable rather than pretending to have answered with AI.

## Run locally

Clone the repository:

```bash
git clone https://github.com/abrahamzion01/support-automation-tool.git
cd support-automation-tool
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

### Support request

```bash
python3 main.py "I was charged twice for my subscription"
```

The system classifies the request, retrieves relevant company guidance, generates a grounded draft when OpenAI is available, and shows the evidence and review state.

### Human review

```bash
python3 main.py "I was charged twice for my subscription" --review
```

The reviewer can:

- `a` — approve the generated draft;
- `e` — edit the draft;
- `r` — reject the draft.

No action sends a message to a customer automatically.

### General AI chat

Start a multi-turn conversation:

```bash
python3 main.py --chat
```

Example:

```text
AI chat started. Type 'exit' to stop.

You: What is recursion?
Assistant: Recursion is when a function solves a problem by calling itself...

You: Explain it like I'm a beginner.
Assistant: Think of recursion as...
```

The conversation object keeps a bounded number of recent turns so the AI can understand follow-up questions without allowing history to grow indefinitely.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

Tests cover classification, routing, conversation memory, retrieval, drafting, the unified chat flow, the OpenAI integration without real API calls, the end-to-end support pipeline, and human review.

GitHub Actions runs the test suite on pushes and pull requests. CI does not require an OpenAI API key because AI calls are mocked in tests.

## How routing works

The router deliberately uses a conservative approach:

```text
Strong support evidence
        ↓
     SUPPORT
        ↓
Company knowledge base
        ↓
Grounded response
```

General signals or questions that do not look like company support requests are routed to conversational AI:

```text
General question
      ↓
   GENERAL
      ↓
OpenAI + conversation history
```

If the router is uncertain but there is some support evidence, it keeps the message in support mode so company-specific knowledge can still be applied safely.

## AI safety and reliability

### 1. Human approval is mandatory for support drafts

The system generates drafts only. The review layer has no customer messaging integration.

### 2. Retrieval remains the source of truth for company support

OpenAI receives retrieved knowledge for support requests instead of being allowed to invent company policies. The model is instructed not to invent refunds, prices, timelines, guarantees, or credentials.

### 3. AI failure does not break support automation

Missing API keys, missing SDKs, API failures, and empty model responses are represented as `AIUnavailable`. Support drafting then falls back to the deterministic local response path.

### 4. Weak evidence is visible

Classification confidence and retrieval confidence are separate signals. An uncertain classification or weak knowledge match sets `review_required=True`.

### 5. Conversation memory is bounded

Only a fixed number of recent user/assistant messages are retained in memory. This prevents unbounded growth and keeps prompts manageable.

### 6. Secrets stay out of source control

API credentials are loaded from `OPENAI_API_KEY` and `.env` is ignored by Git. No secret belongs in the repository.

## Engineering decisions to understand

The main engineering work in the current implementation includes:

1. **Classifier confidence calibration** — confidence considers evidence strength and ambiguity instead of treating a single weak keyword as highly certain.
2. **Safer retrieval** — knowledge-base search supports category filtering and minimum similarity thresholds with deterministic ordering.
3. **Grounded drafting** — support drafts expose confidence, sources, and review state so a human can distinguish evidence from uncertainty.
4. **OpenAI integration** — the AI layer is isolated from business logic and has a deterministic support fallback.
5. **Conversational routing** — general questions can use OpenAI without bypassing the company-support knowledge workflow.
6. **Conversation memory** — follow-up questions can use recent conversation context while keeping history bounded.
7. **End-to-end testing** — tests verify the request → routing → classification/retrieval → drafting → review behavior, including mocked AI calls.
8. **Reproducibility** — CI does not depend on a live model call, database, or external support service.

Be prepared to explain the confidence calculation, TF-IDF retrieval, routing decision, conversation memory, how retrieved context is passed to OpenAI, why support answers remain grounded, and how the fallback works.

## Future improvements

- AI-assisted classification with structured model output and deterministic fallback.
- Semantic/vector retrieval while retaining source tracking.
- A web/API interface for support agents.
- Persistent conversation storage with privacy controls.
- Structured audit logs for review decisions.
- Evaluation datasets and metrics for routing, retrieval, groundedness, and response quality.
- Rate limiting and AI cost controls.
- Authentication and role-based access before production deployment.
