"""OpenAI integration with safe local fallbacks."""

import os

from dotenv import load_dotenv

from .conversation import Message

load_dotenv()

DEFAULT_MODEL = "gpt-5.6-luna"


class AIUnavailable(RuntimeError):
    """Raised when the OpenAI client cannot be used."""


def _client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise AIUnavailable("The openai package is not installed.") from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise AIUnavailable("OPENAI_API_KEY is not configured.")

    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _generate(prompt: str) -> str:
    client = _client()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    response = client.responses.create(model=model, input=prompt)
    text = response.output_text.strip()
    if not text:
        raise AIUnavailable("OpenAI returned an empty response.")
    return text


def generate_grounded_draft(request: str, category: str, sources: list[dict[str, str]]) -> str:
    """Generate a support draft using only supplied knowledge-base content."""
    knowledge = "\n\n".join(
        f"[{source['id']}] {source['title']}: {source['content']}"
        for source in sources
    )
    prompt = f"""You are a customer-support response drafter.

Customer request:
{request}

Predicted category:
{category}

Verified knowledge-base material:
{knowledge}

Write a concise, professional response for a human support agent to review.
Use only facts supported by the supplied knowledge-base material.
If the material does not answer the request, explicitly say that more review is needed.
Never invent policies, refunds, timelines, prices, or guarantees.
Never ask for passwords, API keys, or other secret credentials.
Do not claim that the response was sent.
"""
    return _generate(prompt)


def generate_general_response(message: str, history: list[Message]) -> str:
    """Generate a general conversational answer using bounded conversation history."""
    conversation = "\n".join(f"{item.role}: {item.content}" for item in history)
    prompt = f"""You are a helpful general-purpose AI assistant inside a support automation tool.

Conversation history:
{conversation}

Latest user message:
{message}

Answer the user's question clearly and naturally. Use the conversation history when relevant.
Do not pretend to have taken actions you did not take. Do not request passwords, API keys,
or other secret credentials. If the user asks a company-specific support question, explain
that verified company guidance should be used rather than inventing a policy.
"""
    return _generate(prompt)
