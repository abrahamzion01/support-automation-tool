"""Local knowledge-base loading and deterministic retrieval."""

from dataclasses import dataclass
import json
import math
import re
from pathlib import Path


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    category: str
    content: str


@dataclass(frozen=True)
class SearchResult:
    article: Article
    score: float


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class KnowledgeBase:
    def __init__(self, articles: list[Article]):
        self.articles = articles
        self._documents = [_tokens(f"{a.title} {a.category} {a.content}") for a in articles]
        self._document_frequency: dict[str, int] = {}
        for document in self._documents:
            for token in set(document):
                self._document_frequency[token] = self._document_frequency.get(token, 0) + 1

    @classmethod
    def from_json(cls, path: str | Path) -> "KnowledgeBase":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        articles = [Article(**item) for item in data]
        return cls(articles)

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query_tokens = _tokens(query)
        if not query_tokens:
            return []

        query_counts = {token: query_tokens.count(token) for token in set(query_tokens)}
        query_vector = self._tfidf(query_counts, len(query_tokens))
        results: list[SearchResult] = []

        for article, document in zip(self.articles, self._documents):
            counts = {token: document.count(token) for token in set(document)}
            vector = self._tfidf(counts, len(document))
            score = self._cosine(query_vector, vector)
            if score > 0:
                results.append(SearchResult(article, round(score, 4)))

        results.sort(key=lambda result: result.score, reverse=True)
        return results[:limit]

    def _tfidf(self, counts: dict[str, int], length: int) -> dict[str, float]:
        total_documents = len(self.articles)
        return {
            token: (count / max(length, 1))
            * math.log((1 + total_documents) / (1 + self._document_frequency.get(token, 0)))
            for token, count in counts.items()
        }

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        common = set(left) & set(right)
        numerator = sum(left[token] * right[token] for token in common)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
