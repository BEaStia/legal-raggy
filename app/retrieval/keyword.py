"""Keyword-based retriever for local corpus."""

import re
from collections import Counter
from pathlib import Path

from app.ingestion.chunking import load_corpus
from app.models.retrieval import DocumentChunk, RetrievedChunk

_STOP_WORDS_RU = frozenset(
    [
        "и",
        "в",
        "не",
        "на",
        "с",
        "по",
        "для",
        "это",
        "что",
        "как",
        "или",
        "а",
        "но",
        "из",
        "о",
        "от",
        "до",
        "же",
        "бы",
        "ли",
        "то",
        "так",
        "все",
        "его",
        "она",
        "они",
        "мы",
        "вы",
        "он",
        "она",
        "при",
        "к",
        "у",
        "об",
        "без",
        "через",
        "после",
        "перед",
        "между",
        "под",
        "над",
        "за",
        "про",
        "если",
        "когда",
        "где",
        "который",
        "такой",
        "этот",
        "тот",
        "другой",
        "сам",
        "себя",
        "свой",
        "наш",
        "ваш",
        "их",
        "мой",
        "твой",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "don",
        "now",
        "and",
        "but",
        "or",
        "if",
        "because",
        "while",
        "about",
        "against",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "they",
        "them",
        "their",
        "what",
        "which",
        "who",
        "whom",
        "whose",
    ]
)


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumeric, filter stop words and short tokens."""
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())
    return [t for t in tokens if len(t) > 2 and t not in _STOP_WORDS_RU]


def _keyword_score(query_tokens: list[str], chunk_text: str) -> float:
    """Score a chunk against query tokens using term frequency with heading boost."""
    if not query_tokens:
        return 0.0

    text_tokens = _tokenize(chunk_text)
    if not text_tokens:
        return 0.0

    token_counts = Counter(text_tokens)
    query_set = set(query_tokens)

    score = 0.0
    matched = []
    for token in query_tokens:
        if token in token_counts:
            score += token_counts[token]
            matched.append(token)

    if not matched:
        return 0.0

    doc_length = len(text_tokens)
    tf_norm = score / (doc_length + 1)

    heading_boost = 1.0
    if chunk_text.startswith("#"):
        heading_line = chunk_text.split("\n")[0]
        heading_tokens = _tokenize(heading_line)
        heading_matches = sum(1 for t in query_set if t in heading_tokens)
        if heading_matches:
            heading_boost = 1.0 + (heading_matches * 0.5)

    return round(tf_norm * heading_boost, 4)


class KeywordRetriever:
    """Simple keyword-based retriever over local Markdown corpus."""

    def __init__(self, corpus_dirs: list[Path] | None = None) -> None:
        """Initialize retriever with corpus directories.

        Args:
            corpus_dirs: List of directories to load Markdown files from.
                         Defaults to data/raw/laws and data/raw/architecture_cards
                         relative to project root.
        """
        self._chunks: list[DocumentChunk] = []
        if corpus_dirs:
            self.load_dirs(corpus_dirs)

    def load_dirs(self, dirs: list[Path]) -> None:
        """Load and index chunks from multiple directories."""
        for d in dirs:
            if d.is_dir():
                self._chunks.extend(load_corpus(d))

    def load_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Load chunks directly (useful for testing)."""
        self._chunks = list(chunks)

    @property
    def chunks(self) -> list[DocumentChunk]:
        return list(self._chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Search corpus for chunks matching the query.

        Args:
            query: Search query text.
            top_k: Maximum number of results to return.

        Returns:
            List of RetrievedChunk ordered by score descending.
        """
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scored: list[tuple[float, DocumentChunk, list[str]]] = []
        for chunk in self._chunks:
            score = _keyword_score(query_tokens, chunk.text)
            if score > 0:
                chunk_tokens = _tokenize(chunk.text)
                matched = [t for t in query_tokens if t in chunk_tokens]
                scored.append((score, chunk, matched))

        scored.sort(key=lambda x: (-x[0], x[1].chunk_id))

        return [
            RetrievedChunk(
                chunk=chunk,
                score=score,
                match_reason=", ".join(dict.fromkeys(matched)) if matched else None,
            )
            for score, chunk, matched in scored[:top_k]
        ]
